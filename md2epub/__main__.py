from __future__ import annotations

import logging
import os
import sys
from pathlib import Path

import click

from md2epub import __version__
from md2epub.utils.utils import catch_exception, setup_logging

PYTHON_VERSION = f"{sys.version_info.major}.{sys.version_info.minor}"
PKG_DIR = os.path.dirname(os.path.abspath(__file__))

# Setup logging for the first time and get logger
logger = setup_logging()

# region Default options


def add_options(*opts):
    def inner(f):
        for i in reversed(opts):
            f = i(f)
        return f

    return inner


def verbose_option(f):
    def callback(ctx, param, value):
        if value:
            logger.setLevel(logging.DEBUG)

    return click.option(
        "-v",
        "--verbose",
        is_flag=True,
        expose_value=False,
        help="Enable verbose output",
        callback=callback,
    )(f)


def quiet_option(f):
    def callback(ctx, param, value):
        if value:
            logger.setLevel(logging.CRITICAL)

    return click.option(
        "-q",
        "--quiet",
        is_flag=True,
        expose_value=False,
        help="Silence warnings",
        callback=callback,
    )(f)


common_options = add_options(quiet_option, verbose_option)
context_settings = {"help_option_names": ["-h", "--help"], "max_content_width": 120}

version_msg = f"%(prog)s, version %(version)s from {PKG_DIR} (Python {PYTHON_VERSION})"
build_cmd_short_help = "Compile epub from input MANIFEST file into output EPUB_FILE."
build_cmd_overwrite_help = "overwrite EPUB_FILE ePub if exists."


# region Cli group


@click.group(context_settings=context_settings)
@common_options
@click.version_option(
    __version__,
    "-V",
    "--version",
    message=version_msg,
)
def cli():
    """Md2ePub - Create ePubs easily from Markdown files."""


# region Build command

build_input_type = click.Path(exists=True, resolve_path=True, path_type=Path)
build_output_type = click.Path(exists=False, writable=True, resolve_path=True, path_type=Path)


@cli.command(name="build")
@click.argument("input", type=build_input_type, default=None, required=False, metavar="MANIFEST")
@click.argument("output", type=build_output_type, default=None, required=False, metavar="EPUB_FILE")
@click.option("--overwrite", is_flag=True, default=False, help=build_cmd_overwrite_help)
@common_options
@catch_exception(handle=(Exception))
def build_command(**kwargs):
    """
    Compile epub from input MANIFEST file into output EPUB_FILE.

    MANIFEST can be YAML or JSON file or valid directory. If MANIFEST is:

    - valid file, than this file has been read as input configuration and its parent
    folder will be set as `work_dir`,

    - valid directory, than within this directory one of theese `md2epub.yml|yaml|json`,
    `manifest.yml|yaml|json` are search and the MANIFEST directory will be set as `work_dir`,

    - None, than current directory is set as valid directory and than the same behaviour
    is expected.

    EPUB_FILE is output, which can be set to:

    - valid file, than this file is the output,

    - valid directory, than name of the directory is output file name with `.epub` extension,

    - None, than first, MANIFEST name is checked and if its not default (`md2epub` or `manifest`),
    than this name is used, else, name of the parent directory is user with `.epub` extension.
    """

    from .commands import build

    build.run(**kwargs)


if __name__ == "__main__":
    cli()
