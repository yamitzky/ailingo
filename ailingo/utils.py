import logging
import sys
from logging import Formatter, StreamHandler


def setup_logger(name: str) -> logging.Logger:
    """
    Set up logger
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # ストリームハンドラの設定
    handler = StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    formatter = Formatter("[%(levelname)s] %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    return logger
