"""
Janela principal do ZyphorixVoice v0.2.0.

Interface redesenhada com seletores de idioma, comboboxes de dispositivo,
VU Meter em tempo real (20fps) e persistência automática de preferências.
"""

from pathlib import Path
from typing import Callable

import customtkinter as ctk
from PIL import Image

from app.audio.device_manager import AudioDevice, AudioDeviceManager
from app.config.persistence import UserPreferences
from app.config.settings import SUPPORTED_LANGUAGES, settings
from app.utils.logger import get_logger


logger = get_logger("ui.main_window")

_ASSETS_DIR = Path(__file__).resolve().parents[2] / "assets"

# ── Paleta de cores ───────────────────────────────────────────
_BG          = "#0d0d1a"
_SURFACE     = "#14142b"
_SURFACE2    = "#1a1a35"
_PRIMARY     = "#a855f7"
_PRIMARY_H   = "#9333ea"
_DANGER      = "#ef4444"
_DANGER_H    = "#dc2626"
_TEXT        = "#e2e8f0"
_SUBTEXT     = "#94a3b8"
_BORDER      = "#1e1e3f"
_STATUS_IDLE = "#64748b"
_STATUS_RUN  = "#22c55e"
_VU_LOW      = "#22c55e"   # verde
_VU_MID      = "#eab308"   # amarelo
_VU_HIGH     = "#ef4444"   # vermelho

_VU_FPS_MS = 50   # atualização a cada 50ms → 20fps


class MainWindow(ctk.CTk):
    """
    Janela principal da aplicação — v0.2.0.

    Recebe AudioDeviceManager e UserPreferences injetados via construtor,
    mantendo a janela desacoplada da lógica de negócio.
    """

    def __init__(
        self,
        device_manager: AudioDeviceManager,
        preferences: UserPreferences,
        on_start: Callable[[], None] | None = None,
        on_stop: Callable[[], None] | None = None,
    ) -> None:
        super().__init__()

        self._dm = device_manager
        self._prefs = preferences
        self._on_start = on_start
        self._on_stop = on_stop
        self._is_running = False
        self._is_testing = False
        self._input_devices: list[AudioDevice] = []
        self._output_devices: list[AudioDevice] = []

        self._configure_window()
        self._build_ui()
        self._load_devices()
        self._restore_preferences()
        self._start_vu_loop()

        logger.info("Janela principal v0.2.0 inicializada.")

    # ── Configuração da janela ────────────────────────────────

    def _configure_window(self) -> None:
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.title(f"{settings.app.app_name}  v{settings.app.version}")
        self.geometry("480x790")
        self.resizable(False, False)
        self.configure(fg_color=_BG)

        self.update_idletasks()
        x = (self.winfo_screenwidth() - 480) // 2
        y = (self.winfo_screenheight() - 790) // 2
        self.geometry(f"480x790+{x}+{y}")
        self.lift()
        self.attributes("-topmost", True)
        self.after(200, lambda: self.attributes("-topmost", False))
        self.focus_force()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── Construção da UI ──────────────────────────────────────

    def _build_ui(self) -> None:
        self._build_header()
        self._build_language_selectors()
        self._build_device_selectors()
        self._build_vu_meter()
        self._build_status_panel()
        self._build_controls()
        self._build_footer()

    def _build_header(self) -> None:
        """Header compacto: logo + título."""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(pady=(20, 0))

        logo_path = _ASSETS_DIR / "logo.png"
        if logo_path.exists():
            pil_img = Image.open(logo_path)
            logo_img = ctk.CTkImage(light_image=pil_img, dark_image=pil_img, size=(80, 80))
            ctk.CTkLabel(frame, image=logo_img, text="").pack()
        else:
            ctk.CTkLabel(
                frame, text="🎙",
                font=ctk.CTkFont(size=48), text_color=_PRIMARY,
            ).pack()

        ctk.CTkLabel(
            frame,
            text="ZyphorixVoice",
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=_TEXT,
        ).pack(pady=(8, 0))

        ctk.CTkLabel(
            frame,
            text="Tradutor de Voz em Tempo Real",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=_SUBTEXT,
        ).pack(pady=(2, 0))

        ctk.CTkFrame(self, height=1, fg_color=_BORDER).pack(fill="x", padx=40, pady=(16, 0))

    def _build_language_selectors(self) -> None:
        """Dois comboboxes de idioma lado a lado (entrada / saída)."""
        card = ctk.CTkFrame(self, fg_color=_SURFACE, corner_radius=12)
        card.pack(fill="x", padx=40, pady=(12, 0))
        card.grid_columnconfigure(0, weight=1)
        card.grid_columnconfigure(1, weight=1)

        language_names = list(SUPPORTED_LANGUAGES.keys())

        # Entrada
        left = ctk.CTkFrame(card, fg_color="transparent")
        left.grid(row=0, column=0, padx=(16, 8), pady=12, sticky="ew")

        ctk.CTkLabel(
            left, text="🗣  ENTRADA",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color=_SUBTEXT,
        ).pack(anchor="w")

        self._src_lang_var = ctk.StringVar(value="Português")
        self._src_lang_cb = ctk.CTkComboBox(
            left, values=language_names,
            variable=self._src_lang_var, width=170,
            fg_color=_SURFACE2, border_color=_BORDER,
            button_color=_PRIMARY, button_hover_color=_PRIMARY_H,
            dropdown_fg_color=_SURFACE, text_color=_TEXT,
            command=lambda v: self._prefs.set("source_language", v),
        )
        self._src_lang_cb.pack(anchor="w", pady=(4, 0))

        # Saída
        right = ctk.CTkFrame(card, fg_color="transparent")
        right.grid(row=0, column=1, padx=(8, 16), pady=12, sticky="ew")

        ctk.CTkLabel(
            right, text="🌐  SAÍDA",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color=_SUBTEXT,
        ).pack(anchor="w")

        self._tgt_lang_var = ctk.StringVar(value="English")
        self._tgt_lang_cb = ctk.CTkComboBox(
            right, values=language_names,
            variable=self._tgt_lang_var, width=170,
            fg_color=_SURFACE2, border_color=_BORDER,
            button_color=_PRIMARY, button_hover_color=_PRIMARY_H,
            dropdown_fg_color=_SURFACE, text_color=_TEXT,
            command=lambda v: self._prefs.set("target_language", v),
        )
        self._tgt_lang_cb.pack(anchor="w", pady=(4, 0))

    def _build_device_selectors(self) -> None:
        """Comboboxes de microfone e saída de áudio."""
        card = ctk.CTkFrame(self, fg_color=_SURFACE, corner_radius=12)
        card.pack(fill="x", padx=40, pady=(12, 0))

        # Microfone
        ctk.CTkLabel(
            card, text="🎤  MICROFONE",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color=_SUBTEXT,
        ).pack(anchor="w", padx=16, pady=(12, 2))

        self._mic_var = ctk.StringVar(value="Detectando...")
        self._mic_cb = ctk.CTkComboBox(
            card, values=["Detectando..."],
            variable=self._mic_var, width=408,
            fg_color=_SURFACE2, border_color=_BORDER,
            button_color=_PRIMARY, button_hover_color=_PRIMARY_H,
            dropdown_fg_color=_SURFACE, text_color=_TEXT,
            command=self._on_mic_change,
        )
        self._mic_cb.pack(anchor="w", padx=16)

        # Saída
        ctk.CTkLabel(
            card, text="🔊  SAÍDA DE ÁUDIO",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color=_SUBTEXT,
        ).pack(anchor="w", padx=16, pady=(10, 2))

        self._out_var = ctk.StringVar(value="Detectando...")
        self._out_cb = ctk.CTkComboBox(
            card, values=["Detectando..."],
            variable=self._out_var, width=408,
            fg_color=_SURFACE2, border_color=_BORDER,
            button_color=_PRIMARY, button_hover_color=_PRIMARY_H,
            dropdown_fg_color=_SURFACE, text_color=_TEXT,
            command=self._on_output_change,
        )
        self._out_cb.pack(anchor="w", padx=16, pady=(0, 12))

    def _build_vu_meter(self) -> None:
        """Barra de nível de áudio + botão Testar."""
        card = ctk.CTkFrame(self, fg_color=_SURFACE, corner_radius=12)
        card.pack(fill="x", padx=40, pady=(12, 0))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(12, 6))

        ctk.CTkLabel(
            row, text="📊  NÍVEL DO MICROFONE",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color=_SUBTEXT,
        ).pack(side="left")

        self._btn_test = ctk.CTkButton(
            row, text="⚡ Testar",
            width=90, height=26, corner_radius=6,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=_SURFACE2, hover_color=_PRIMARY_H,
            text_color=_SUBTEXT, border_width=1, border_color=_BORDER,
            command=self._handle_test,
        )
        self._btn_test.pack(side="right")

        self._vu_bar = ctk.CTkProgressBar(
            card, width=408, height=14,
            corner_radius=4,
            fg_color=_SURFACE2,
            progress_color=_VU_LOW,
        )
        self._vu_bar.set(0)
        self._vu_bar.pack(padx=16, pady=(0, 12))

    def _build_status_panel(self) -> None:
        """Painel de status da aplicação."""
        card = ctk.CTkFrame(self, fg_color=_SURFACE, corner_radius=12)
        card.pack(fill="x", padx=40, pady=(12, 0))

        ctk.CTkLabel(
            card, text="⬤  STATUS",
            font=ctk.CTkFont(family="Segoe UI", size=9, weight="bold"),
            text_color=_SUBTEXT,
        ).pack(anchor="w", padx=16, pady=(10, 2))

        self._status_label = ctk.CTkLabel(
            card,
            text="Aguardando...",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=_STATUS_IDLE,
        )
        self._status_label.pack(anchor="w", padx=16, pady=(0, 10))

    def _build_controls(self) -> None:
        """Botões Iniciar e Parar."""
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.pack(pady=(16, 0))

        self._btn_start = ctk.CTkButton(
            frame, text="▶  Iniciar",
            width=160, height=48, corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color=_PRIMARY, hover_color=_PRIMARY_H,
            command=self._handle_start,
        )
        self._btn_start.grid(row=0, column=0, padx=10)

        self._btn_stop = ctk.CTkButton(
            frame, text="■  Parar",
            width=160, height=48, corner_radius=10,
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            fg_color=_SURFACE, hover_color=_DANGER_H,
            text_color=_SUBTEXT, border_width=1, border_color=_BORDER,
            state="disabled",
            command=self._handle_stop,
        )
        self._btn_stop.grid(row=0, column=1, padx=10)

    def _build_footer(self) -> None:
        ctk.CTkLabel(
            self,
            text=f"v{settings.app.version}  •  ZyphorixVoice",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=_BORDER,
        ).pack(side="bottom", pady=10)

    # ── Carregamento de dispositivos ──────────────────────────

    def _load_devices(self) -> None:
        """Popula os comboboxes com os dispositivos detectados."""
        self._input_devices = self._dm.get_input_devices()
        self._output_devices = self._dm.get_output_devices()

        in_names = [d.name for d in self._input_devices]
        out_names = [d.name for d in self._output_devices]

        self._mic_cb.configure(values=in_names or ["Nenhum microfone encontrado"])
        self._out_cb.configure(values=out_names or ["Nenhum dispositivo encontrado"])

        if in_names:
            self._mic_var.set(in_names[0])
        if out_names:
            self._out_var.set(out_names[0])

        logger.info(f"Dispositivos: {len(in_names)} entrada(s), {len(out_names)} saída(s).")

    def _restore_preferences(self) -> None:
        """Restaura seleções salvas do usuário."""
        in_names = [d.name for d in self._input_devices]
        out_names = [d.name for d in self._output_devices]

        saved_mic = self._prefs.get("input_device_name")
        if saved_mic and saved_mic in in_names:
            self._mic_var.set(saved_mic)

        saved_out = self._prefs.get("output_device_name")
        if saved_out and saved_out in out_names:
            self._out_var.set(saved_out)

        lang_names = list(SUPPORTED_LANGUAGES.keys())

        src = self._prefs.get("source_language")
        if src and src in lang_names:
            self._src_lang_var.set(src)

        tgt = self._prefs.get("target_language")
        if tgt and tgt in lang_names:
            self._tgt_lang_var.set(tgt)

    # ── Handlers de eventos ───────────────────────────────────

    def _on_mic_change(self, name: str) -> None:
        self._prefs.set("input_device_name", name)
        if self._is_testing:
            self._start_test_for(name)
        logger.info(f"Microfone: {name}")

    def _on_output_change(self, name: str) -> None:
        self._prefs.set("output_device_name", name)
        logger.info(f"Saída: {name}")

    def _handle_test(self) -> None:
        if self._is_testing:
            self._stop_test()
        else:
            self._start_test_for(self._mic_var.get())

    def _start_test_for(self, mic_name: str) -> None:
        device = next((d for d in self._input_devices if d.name == mic_name), None)
        if device is None:
            logger.warning("Dispositivo de teste não encontrado.")
            return

        self._is_testing = True
        self._btn_test.configure(
            text="⏹ Parar", fg_color=_DANGER,
            text_color=_TEXT, border_width=0,
        )
        self._dm.start_monitoring(device.id)
        self._update_status("Testando microfone...", running=True)
        logger.info(f"Teste iniciado: {mic_name}")

    def _stop_test(self) -> None:
        self._is_testing = False
        self._dm.stop_monitoring()
        self._vu_bar.set(0)
        self._vu_bar.configure(progress_color=_VU_LOW)
        self._btn_test.configure(
            text="⚡ Testar", fg_color=_SURFACE2,
            text_color=_SUBTEXT, border_width=1,
        )
        if not self._is_running:
            self._update_status("Aguardando...")
        logger.info("Teste encerrado.")

    def _handle_start(self) -> None:
        if self._is_running:
            return
        if self._is_testing:
            self._stop_test()

        self._is_running = True
        self._update_status("Ativo — traduzindo...", running=True)
        self._btn_start.configure(state="disabled", fg_color=_SURFACE, text_color=_SUBTEXT)
        self._btn_stop.configure(state="normal", fg_color=_DANGER, text_color=_TEXT)
        logger.info("Tradução iniciada.")

        if self._on_start:
            self._on_start()

    def _handle_stop(self) -> None:
        if not self._is_running:
            return

        self._is_running = False
        self._update_status("Parado.")
        self._btn_start.configure(state="normal", fg_color=_PRIMARY, text_color=_TEXT)
        self._btn_stop.configure(state="disabled", fg_color=_SURFACE, text_color=_SUBTEXT)
        logger.info("Tradução parada.")

        if self._on_stop:
            self._on_stop()

    def _on_close(self) -> None:
        logger.info("Encerrando aplicação.")
        self._stop_test()
        self.destroy()

    # ── Loop do VU Meter ──────────────────────────────────────

    def _start_vu_loop(self) -> None:
        """Inicia o loop de atualização a 20fps via after()."""
        self._update_vu()

    def _update_vu(self) -> None:
        """Atualiza a barra de nível e sua cor a cada _VU_FPS_MS ms."""
        level = self._dm.get_level()
        self._vu_bar.set(level)

        if level < 0.6:
            color = _VU_LOW
        elif level < 0.8:
            color = _VU_MID
        else:
            color = _VU_HIGH

        self._vu_bar.configure(progress_color=color)
        self.after(_VU_FPS_MS, self._update_vu)

    # ── API pública ───────────────────────────────────────────

    def _update_status(self, message: str, running: bool = False) -> None:
        color = _STATUS_RUN if running else _STATUS_IDLE
        self._status_label.configure(text=message, text_color=color)

    def set_status(self, message: str, running: bool = False) -> None:
        """Atualiza o status externamente."""
        self._update_status(message, running)
