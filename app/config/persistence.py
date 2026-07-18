"""
Persistência de preferências do usuário.

Salva e carrega automaticamente configurações de sessão (dispositivos
e idiomas) em user_prefs.json — arquivo ignorado pelo git.
"""

import json
from pathlib import Path
from typing import Any

from app.utils.logger import get_logger


logger = get_logger("config.persistence")

_PREFS_FILE = Path(__file__).resolve().parents[2] / "user_prefs.json"

_DEFAULTS: dict[str, Any] = {
    "input_device_name": None,
    "output_device_name": None,
    "source_language": "Português",
    "target_language": "English",
}


class UserPreferences:
    """
    Lê e persiste preferências do usuário em user_prefs.json.

    Exemplo:
        prefs = UserPreferences()
        prefs.set("input_device_name", "HyperX QuadCast")
        nome = prefs.get("input_device_name")
    """

    def __init__(self) -> None:
        self._data: dict[str, Any] = dict(_DEFAULTS)
        self._load()

    def _load(self) -> None:
        if _PREFS_FILE.exists():
            try:
                with open(_PREFS_FILE, encoding="utf-8") as f:
                    stored = json.load(f)
                self._data.update(stored)
                logger.debug("Preferências carregadas.")
            except Exception as exc:
                logger.warning(f"Não foi possível carregar preferências: {exc}")

    def _save(self) -> None:
        try:
            with open(_PREFS_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except Exception as exc:
            logger.error(f"Erro ao salvar preferências: {exc}")

    def get(self, key: str) -> Any:
        """Retorna o valor de uma preferência pelo nome da chave."""
        return self._data.get(key, _DEFAULTS.get(key))

    def set(self, key: str, value: Any) -> None:
        """Define e persiste imediatamente uma preferência."""
        self._data[key] = value
        self._save()
        logger.debug(f"Preferência salva: {key}={value!r}")
