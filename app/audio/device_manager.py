"""
Gerenciador de dispositivos de áudio.

Detecta microfones e dispositivos de saída, controla o stream de
monitoramento para o VU Meter e expõe o nível RMS de forma thread-safe.
"""

import threading
from dataclasses import dataclass
from typing import Any

import numpy as np
import sounddevice as sd

from app.utils.logger import get_logger


logger = get_logger("audio.device_manager")


@dataclass(frozen=True)
class AudioDevice:
    """Representa um dispositivo de áudio do sistema."""

    id: int
    name: str
    channels: int

    def __str__(self) -> str:
        return self.name


class AudioDeviceManager:
    """
    Gerencia dispositivos de áudio e o stream de monitoramento do VU Meter.

    O stream de áudio roda em thread dedicada (sounddevice).
    O nível RMS é atualizado via callback e lido com get_level() — thread-safe.
    """

    def __init__(self) -> None:
        self._stream: sd.InputStream | None = None
        self._lock = threading.Lock()
        self._level: float = 0.0
        logger.info("AudioDeviceManager inicializado.")

    # ── Listagem de dispositivos ──────────────────────────────

    def get_input_devices(self) -> list[AudioDevice]:
        """Retorna todos os dispositivos de entrada (microfones)."""
        devices: list[AudioDevice] = []
        try:
            for idx, dev in enumerate(sd.query_devices()):
                if dev["max_input_channels"] > 0:
                    devices.append(AudioDevice(
                        id=idx,
                        name=dev["name"],
                        channels=dev["max_input_channels"],
                    ))
        except Exception as exc:
            logger.error(f"Erro ao listar entradas: {exc}")

        logger.debug(f"{len(devices)} dispositivo(s) de entrada encontrado(s).")
        return devices

    def get_output_devices(self) -> list[AudioDevice]:
        """Retorna todos os dispositivos de saída."""
        devices: list[AudioDevice] = []
        try:
            for idx, dev in enumerate(sd.query_devices()):
                if dev["max_output_channels"] > 0:
                    devices.append(AudioDevice(
                        id=idx,
                        name=dev["name"],
                        channels=dev["max_output_channels"],
                    ))
        except Exception as exc:
            logger.error(f"Erro ao listar saídas: {exc}")

        logger.debug(f"{len(devices)} dispositivo(s) de saída encontrado(s).")
        return devices

    def get_default_input_id(self) -> int | None:
        """Retorna o ID do microfone padrão do sistema."""
        try:
            default = sd.query_devices(kind="input")
            for idx, dev in enumerate(sd.query_devices()):
                if dev["name"] == default["name"]:
                    return idx
        except Exception:
            pass
        return None

    def get_default_output_id(self) -> int | None:
        """Retorna o ID do dispositivo de saída padrão do sistema."""
        try:
            default = sd.query_devices(kind="output")
            for idx, dev in enumerate(sd.query_devices()):
                if dev["name"] == default["name"]:
                    return idx
        except Exception:
            pass
        return None

    # ── Stream de monitoramento ───────────────────────────────

    def start_monitoring(self, device_id: int, sample_rate: int = 16000) -> None:
        """
        Inicia o stream de monitoramento (VU Meter).

        Args:
            device_id: ID do dispositivo de entrada.
            sample_rate: Taxa de amostragem em Hz.
        """
        self.stop_monitoring()

        def _callback(
            indata: np.ndarray,
            frames: int,
            time: Any,
            status: sd.CallbackFlags,
        ) -> None:
            if status:
                logger.warning(f"Stream status: {status}")
            rms = float(np.sqrt(np.mean(indata ** 2)))
            # Amplifica e normaliza para 0.0–1.0
            with self._lock:
                self._level = min(rms * 20.0, 1.0)

        try:
            self._stream = sd.InputStream(
                device=device_id,
                channels=1,
                samplerate=sample_rate,
                callback=_callback,
                blocksize=1024,
            )
            self._stream.start()
            logger.info(f"Monitoramento iniciado — dispositivo ID={device_id}.")
        except Exception as exc:
            logger.error(f"Erro ao iniciar stream: {exc}")
            self._stream = None

    def stop_monitoring(self) -> None:
        """Encerra o stream de monitoramento e zera o nível."""
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
                logger.info("Monitoramento encerrado.")
            except Exception as exc:
                logger.error(f"Erro ao encerrar stream: {exc}")
            finally:
                self._stream = None
                with self._lock:
                    self._level = 0.0

    def get_level(self) -> float:
        """Retorna o nível RMS atual normalizado (0.0–1.0)."""
        with self._lock:
            return self._level

    def __del__(self) -> None:
        self.stop_monitoring()
