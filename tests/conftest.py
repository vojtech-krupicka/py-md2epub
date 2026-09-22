"""Shared fixtures for the md2epub test suite."""

from __future__ import annotations

import logging
from pathlib import Path

import pytest
import yaml

from md2epub.commands import build
from md2epub.core.environment import Environment, setup_environment
from tests.helpers import PNG_1X1, SECRET


@pytest.fixture(autouse=True)
def env(tmp_path: Path) -> Environment:
    """
    Fresh `Environment` singleton for every test (the code reads it through `get_environment()`).

    The logger is normally attached by the CLI wrapper from a config file, here a plain logger is enough.
    """
    environment = setup_environment("md2epub-test", version="0.0.0")
    environment.logger = logging.getLogger("md2epub.tests")
    environment.set_work_dir(tmp_path)
    return environment


class Project:
    """A throw-away book project on disk: `<tmp>/proj/` with a manifest and some sources."""

    def __init__(self, root: Path):
        self.root = root
        self.root.mkdir(parents=True, exist_ok=True)
        self.out_dir = root.parent / "out"
        self.out_dir.mkdir(exist_ok=True)
        self.manifest_path = root / "manifest.yaml"

    def write(self, rel: str, content: str | bytes = "") -> Path:
        """Write a file (creating folders) relative to the project root."""
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        if isinstance(content, bytes):
            path.write_bytes(content)
        else:
            path.write_text(content, encoding="utf-8")
        return path

    def manifest(self, *, filename: str = "manifest.yaml", book: dict | None = None, **top) -> Path:
        """
        Write the manifest. `top` overrides top-level keys, `book` is merged into the default `book` key.
        The default book is a TOC page followed by `text/ch1.md`.
        """
        data: dict = {
            "title": "Test Book",
            "author": "Jane Doe",
            "language": "en",
            "book": {"name": "content", "pages": [{"type": "toc"}, "text/ch1.md"]},
        }
        data.update(top)
        if book:
            data["book"] = {**data["book"], **book}

        self.manifest_path = self.root / filename
        self.manifest_path.write_text(yaml.safe_dump(data, allow_unicode=True), encoding="utf-8")
        return self.manifest_path

    def build(self, output: Path | None = None, *, overwrite: bool = True, **kwargs) -> Path:
        """Run the real build command and return the path of the EPUB. `kwargs` forward to `build.run`."""
        output = output or self.out_dir / "book.epub"
        build.run(self.manifest_path, output, overwrite, **kwargs)
        return output


@pytest.fixture
def project(tmp_path: Path) -> Project:
    """A small but complete project: one chapter, a cover image, a stylesheet and a default manifest."""
    p = Project(tmp_path / "proj")
    p.write("text/ch1.md", '# Chapter One\n\nHello *world* & "quotes".\n')
    p.write("images/cover.png", PNG_1X1)
    p.write("styles/s.css", "body { color: black; }\n")
    p.manifest()
    return p


@pytest.fixture
def outside(tmp_path: Path) -> Path:
    """Files next to (but outside of) the project. Nothing in them may ever end up inside an EPUB."""
    folder = tmp_path / "outside"
    folder.mkdir()
    (folder / "secret.md").write_text(f"# Secret\n\n{SECRET}\n", encoding="utf-8")
    (folder / "secret.png").write_bytes(PNG_1X1 + SECRET.encode())
    (folder / "secret.css").write_text(f"/* {SECRET} */\n", encoding="utf-8")
    return folder


@pytest.fixture
def log_cfg(tmp_path: Path) -> Path:
    """A logging config for CLI tests which throws everything away (no real streams, no extra packages)."""
    cfg = tmp_path / "logging.yaml"
    cfg.write_text(
        "version: 1\n"
        "disable_existing_loggers: false\n"
        "handlers:\n"
        "  null:\n"
        "    class: logging.NullHandler\n"
        "root:\n"
        "  level: DEBUG\n"
        "  handlers: [null]\n",
        encoding="utf-8",
    )
    return cfg
