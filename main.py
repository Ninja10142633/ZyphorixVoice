"""
Ponto de entrada da aplicação ZyphorixVoice.

Inicializa o sistema de logs, instancia o AudioDeviceManager e
UserPreferences, e exibe a janela principal.
"""

import sys

from app.audio.device_manager import AudioDeviceManager
from app.config.persistence import UserPreferences
from app.config.settings import settings
from app.ui.main_window import MainWindow
from app.utils.logger import setup_logger


def main() -> None:
    """Inicializa e executa a aplicação."""
    logger = setup_logger()
    logger.info("=" * 60)
    logger.info(f"Iniciando {settings.app.app_name} v{settings.app.version}")
    logger.info(f"Python: {sys.version.split()[0]}")
    logger.info(f"Debug: {settings.app.debug}")
    logger.info("=" * 60)

    device_manager = AudioDeviceManager()
    preferences = UserPreferences()

    try:
        window = MainWindow(
            device_manager=device_manager,
            preferences=preferences,
            on_start=lambda: logger.info("Evento: on_start disparado."),
            on_stop=lambda: logger.info("Evento: on_stop disparado."),
        )
        window.mainloop()
    except Exception as exc:
        logger.exception(f"Erro crítico: {exc}")
        sys.exit(1)
    finally:
        device_manager.stop_monitoring()
        logger.info(f"{settings.app.app_name} encerrado.")


if __name__ == "__main__":
    main()
