# Python Markdown 2 ePub

# A Python implementation of ePub creator from Markdown chapter files.

# Documentation: https://github.com/vojtech-krupicka/md2epub/blob/master/README.md
# GitHub: https://github.com/vojtech-krupicka/md2epub
# PyPI: TBD

# Started by Vojtech Krupicka (<voker@email.cz>).

# Copyright 2024 Vojtech Krupicka

# License: MIT (see LICENSE.md for details).

import os
import sys
from importlib.metadata import PackageNotFoundError, version

# Try to get version from package metadata, if not available, set to "0.0.0"
try:
    __version__ = version("md2epub")
except PackageNotFoundError:
    __version__ = "0.0.0"

# Get some constants
__appname__ = "md2epub"
__python_version__ = f"{sys.version_info.major}.{sys.version_info.minor}"
__pgkdir__ = os.path.dirname(os.path.abspath(__file__))
