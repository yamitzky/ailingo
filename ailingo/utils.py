import logging

from rich.logging import RichHandler


def setup_logger(level: int | None = None):
    """
    Set up logger
    """

    FORMAT = "%(message)s"
    logging.basicConfig(
        level=level, format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
    )
