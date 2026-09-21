from __future__ import annotations

import logging
import logging.config
from pathlib import Path

import yaml

from md2epub import __appname__


def get_logger(name: str | None = None) -> logging.Logger:
    """Get logger by its name as `{__appname__}.{name}`. If no name given, use `root` instead."""
    name = name or "root"
    return logging.getLogger(f"{__appname__}.{name}")


def setup_logging(file: str | Path, name: str | None = None) -> logging.Logger:
    """Setup logging from config file in yaml and get logger."""
    with Path(file).open("r") as ifp:
        config = yaml.safe_load(ifp)

    logging.config.dictConfig(config)
    return get_logger(name)
