"""
Configurações centrais da aplicação ZyphorixVoice.

Carrega variáveis do arquivo .env e expõe dataclasses imutáveis
para consumo por qualquer módulo do projeto.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv


_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

# Idiomas suportados: nome de exibição → código ISO 639-1
SUPPORTED_LANGUAGES: dict[str, str] = {
    "Português": "pt",
    "English": "en",
    "Español": "es",
    "Français": "fr",
    "Deutsch": "de",
    "Italiano": "it",
    "日本語": "ja",
    "中文": "zh",
    "한국어": "ko",
    "Русский": "ru",
    "العربية": "ar",
    "हिन्दी": "hi",
}


@dataclass(frozen=True)
class AppSettings:
    """Configurações gerais da aplicação."""

    app_name: str = "ZyphorixVoice"
    version: str = "0.2.0"
    debug: bool = field(default_factory=lambda: os.getenv("DEBUG", "false").lower() == "true")


@dataclass(frozen=True)
class AudioSettings:
    """Configurações de dispositivos de áudio."""

    default_microphone: str = field(
        default_factory=lambda: os.getenv("DEFAULT_MICROPHONE", "Microfone padrão do sistema")
    )
    sample_rate: int = 16000
    channels: int = 1
    chunk_size: int = 1024


@dataclass(frozen=True)
class TranslationSettings:
    """Configurações do serviço de tradução (a ser implementado na v0.4.0)."""

    source_language: str = field(default_factory=lambda: os.getenv("SOURCE_LANG", "pt"))
    target_language: str = field(default_factory=lambda: os.getenv("TARGET_LANG", "en"))
    engine: str = field(default_factory=lambda: os.getenv("TRANSLATION_ENGINE", "none"))


@dataclass(frozen=True)
class Settings:
    """Objeto raiz de configuração da aplicação."""

    app: AppSettings = field(default_factory=AppSettings)
    audio: AudioSettings = field(default_factory=AudioSettings)
    translation: TranslationSettings = field(default_factory=TranslationSettings)


settings = Settings()
