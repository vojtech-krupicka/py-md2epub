# Python Markdown 2 ePub

# A Python implementation of ePub creator from Markdown chapter files.

# Documentation: https://github.com/vojtech-krupicka/md2epub/blob/master/README.md
# GitHub: https://github.com/vojtech-krupicka/md2epub
# PyPI: TBD

# Started by Vojtech Krupicka (<voker@email.cz>).

# Copyright 2024 Vojtech Krupicka

# License: MIT (see LICENSE.md for details).

import os
import re
import sys
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path


def _version_from_changelog() -> str | None:
    """
    Read the most recent version heading from CHANGELOG.md, e.g. "## [0.1.0] - 2026-09-23".

    This only works from a source checkout (CHANGELOG.md is not shipped inside the installed
    package). It exists for two callers: `pyproject.toml`'s `[tool.setuptools.dynamic]` reads it
    at build time (before the package has any installed metadata to read back), and it is the
    fallback below for running straight from a checkout with no install at all.
    """
    changelog = Path(__file__).resolve().parent.parent / "CHANGELOG.md"
    if not changelog.is_file():
        return None

    match = re.search(r"^## \[(\d+\.\d+\.\d+(?:[-+][\w.]*)?)\]", changelog.read_text(encoding="utf-8"), re.MULTILINE)
    return match.group(1) if match else None


# The installed package's own metadata is the real, fast source of truth at runtime - it holds
# whatever version was baked in at build time (see `_version_from_changelog` above). Only fall
# back to reading CHANGELOG.md directly when there is no install to ask (e.g. PYTHONPATH=. dev use).
try:
    __version__ = version("md2epub")
except PackageNotFoundError:
    __version__ = _version_from_changelog() or "0.0.0"

# Get some constants
__appname__ = "md2epub"
__python_version__ = f"{sys.version_info.major}.{sys.version_info.minor}"
__pgkdir__ = os.path.dirname(os.path.abspath(__file__))
