"""
Ponto de entrada da aplicação ZyphorixVoice.

Inicializa o sistema de logs, carrega configurações e exibe
a janela principal da interface gráfica.
"""

import sys

from app.config.settings import settings
from app.utils.logger import setup_logger
from app.ui.main_window import MainWindow


def main() -> None:
    """Inicializa e executa a aplicação."""
    logger = setup_logger()
    logger.info("=" * 60)
    logger.info(f"Iniciando {settings.app.app_name} v{settings.app.version}")
    logger.info(f"Python: {sys.version.split()[0]}")
    logger.info(f"Debug: {settings.app.debug}")
    logger.info("=" * 60)

    try:
        window = MainWindow(
            on_start=lambda: logger.info("Evento: on_start disparado."),
            on_stop=lambda: logger.info("Evento: on_stop disparado."),
        )
        window.mainloop()
    except Exception as exc:
        logger.exception(f"Erro crítico na aplicação: {exc}")
        sys.exit(1)
    finally:
        logger.info(f"{settings.app.app_name} encerrado.")


if __name__ == "__main__":
    main()
