import logging
import sys
import warnings
from functools import partial, wraps

import click


def get_logger(name: str = "md2epub"):
    return logging.getLogger(name)


def setup_logging(level: int = logging.INFO) -> logging.Logger:
    """
    Setup logging.
    """

    formatter = logging.Formatter(
        '%(asctime)s %(name)s %(levelname)s: "%(message)s" (%(module)s:%(funcName)s:%(lineno)s)'
    )
    handler = logging.StreamHandler(sys.stdout)
    handler.name = "Md2EpubStreamHandler"
    handler.setFormatter(formatter)

    logger = get_logger()
    logger.setLevel(level)
    logger.propagate = False
    logger.addHandler(handler)

    if level <= logging.WARNING:
        # Ensure deprecation warnings get displayed
        warnings.filterwarnings("default")
        logging.captureWarnings(True)
        warn_logger = logging.getLogger("py.warnings")
        warn_logger.addHandler(handler)

    return logger


def catch_exception(func=None, *, handle, message=None):
    if not func:
        return partial(catch_exception, handle=handle)

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except handle as e:
            # if not message:
            message = f"Error occurs in '{func.__name__}' command!"

            get_logger().exception(message)
            # raise click.ClickException(e)

    return wrapper
