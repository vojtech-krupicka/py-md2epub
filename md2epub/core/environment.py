from __future__ import annotations

import logging
from pathlib import Path

from md2epub.utils.logging import get_logger, setup_logging


class Environment:
    def __init__(self, appname: str, version: str, work_dir: str | Path | None = None) -> None:
        self.appname = appname
        self.version = version
        self.package = "md2epub"

        self.trust_extensions: bool = False

        self.static_dir = (Path(__file__).parent / ".." / ".." / "static").resolve()
        self.template_dir = (Path(__file__).parent / ".." / ".." / "templates").resolve()
        self.set_work_dir(work_dir)

    def set_work_dir(self, work_dir: str | Path | None) -> Environment:
        """Set the working directory for the environment."""
        self.work_dir = (Path(work_dir).resolve() if work_dir is not None else Path().cwd()).expanduser()
        return self

    def set_trust_extensions(self, trust_extensions: bool) -> Environment:
        """Trust any Markdown extension named in the manifest, not only the built-in and md2epub ones."""
        self.trust_extensions = trust_extensions
        return self

    # region Setup

    def setup_logger(
        self,
        cfg_file: str | Path,
        name: str | None = None,
        logging_level: str | int = logging.INFO,
    ) -> logging.Logger:
        self.logger = setup_logging(cfg_file, name=name)
        self.logger.setLevel(logging_level)
        return self.logger

    # region Misc

    def get_logger(self, name: str | None = None) -> logging.Logger:
        return get_logger(name)

    def get_version(self) -> str:
        return self.version

    def get_release(self) -> str:
        return f"{self.appname}@{self.get_version()}"


# region Sigleton

_instance: Environment | None = None


def setup_environment(appname: str, version: str) -> Environment:
    global _instance
    _instance = Environment(appname, version)
    return _instance


def get_environment() -> Environment:
    global _instance  # noqa: PLW0602

    if _instance is None:
        raise RuntimeError("Environment is not set up. Call `setup_environment()` first.")

    return _instance
