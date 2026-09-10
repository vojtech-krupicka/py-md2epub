# Python Markdown 2 ePub

# A Python implementation of ePub creator from Markdown chapter files.

# Documentation: https://github.com/vojtech-krupicka/md2epub/blob/master/README.md
# GitHub: https://github.com/vojtech-krupicka/md2epub
# PyPI: TBD

# Started by Vojtech Krupicka (<voker@email.cz>).

# Copyright 2024 Vojtech Krupicka

# License: MIT (see LICENSE.md for details).

from __future__ import annotations

from importlib import resources

import tomllib
from kachlog.utils import ChangelogUtils

from md2epub.models.config import Config

# Get current version from CHANGELOG.md
__version__ = ChangelogUtils().get_current_version()

# Load config file as resource
_cfg = tomllib.loads(resources.read_text("md2epub.conf", "config.toml"))
current_config = Config(**_cfg)
