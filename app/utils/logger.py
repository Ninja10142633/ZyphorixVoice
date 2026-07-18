"""
Sistema de logging centralizado do ZyphorixVoice.

Configura handlers para saída no console e em arquivo rotativo,
garantindo que todos os módulos usem o mesmo formato e destino.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


LOG_DIR = Path(__file__).resolve().parents[2] / "logs"
LOG_FILE = LOG_DIR / "zyphorix.log"
LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


def setup_logger(level: int = logging.DEBUG) -> logging.Logger:
    """
    Configura e retorna o logger raiz da aplicação.

    Args:
        level: Nível de log padrão (ex: logging.DEBUG, logging.INFO).

    Returns:
        Logger raiz configurado com handlers de console e arquivo.
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)

    # Handler para o console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Handler para arquivo com rotação (máx 5MB, 3 backups)
    file_handler = RotatingFileHandler(
        filename=LOG_FILE,
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    root_logger = logging.getLogger("zyphorix")
    root_logger.setLevel(level)
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)
    root_logger.propagate = False

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Retorna um logger filho do logger raiz da aplicação.

    Args:
        name: Nome do módulo/componente (ex: "ui.main_window").

    Returns:
        Logger filho configurado.
    """
    return logging.getLogger(f"zyphorix.{name}")
