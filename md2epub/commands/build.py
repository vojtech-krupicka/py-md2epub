from __future__ import annotations

import re
from pathlib import Path
from typing import Type

import md2epub.utils.utils as Utils
from md2epub import current_config as config
from md2epub.builder import Builder
from md2epub.models.public.manifest import Manifest

logger = Utils.get_logger()


def run(input: Path | None, output: Path | None, overwrite: bool = False):
    logger.info(f"BUILD RUN: {input}, {output}, {overwrite}")

    # Sanitize input and output
    input = _sanitize_input(input)
    output = _sanitize_output(input, output, overwrite)
    logger.info(f"SANITIZED: {input.as_posix()}, {output.as_posix()}")

    # Set current work_dir in config
    config.set_work_dir(input.parent)

    # Create builder
    with Builder() as builder:
        # Load manifest from file and create model
        manifest = Manifest.load_from_file(input)

        # Build ePub from manifest
        builder.build(manifest, output)


def _sanitize_input(input: Path | None) -> Path:
    """
    MANIFEST can be YAML or JSON file or valid directory. If MANIFEST is:

    - valid file, than this file has been read as input configuration and its parent
    folder will be set as `work_dir`,

    - valid directory, than within this directory one of theese `md2epub.yml|yaml|json`,
    `manifest.yml|yaml|json` are search and the MANIFEST directory will be set as `work_dir`,

    - None, than current directory is set as valid directory and than the same behaviour
    is expected.
    """

    # If input is None, get current directory
    if input is None:
        input = Path(".")

    # If input not exists, raise
    if not input.exists():
        raise RuntimeError(f"Manifest not found! Path '{input.as_posix()}' not exists.")

    # If input is valid directory, try to find `md2epub.yml|yaml|json` or `manifest.yml|yaml|json`
    if input.is_dir():
        pattern = re.compile(r"(md2epub|manifest)\.(ya?ml|json)")
        matching_files = [f for f in input.glob("*.*") if pattern.match(f.name)]
        if size := len(matching_files) == 0:
            raise RuntimeError(
                f"Manifest not found! No '{pattern}' file exists within '{input.as_posix()}' directory."
            )
        elif size > 1:
            logger.warning("More than one manifest file found, select the first one...")

        # There is one or more matching manifest files, select the first one
        return matching_files[0]

    # Finaly, input is valid file
    return input


def _sanitize_output(input: Path | None, output: Path | None, overwrite: bool = False) -> Path:
    """
    EPUB_FILE is output, which can be set to:

    - valid file, than this file is the output,

    - valid directory, than name of the directory is output file name with `.epub` extension,

    - None, than first, MANIFEST name is checked and if its not default (`md2epub` or `manifest`),
    than this name is used, else, name of the parent directory is user with `.epub` extension.
    """

    # If output is None, set it to input's parent directory.
    if output is None:
        output = input.parent

    # If output is valid directory, than use this name
    if output.is_dir():
        # Inherit name from input
        if input.stem not in ("md2epub", "manifest"):
            output = (output / input.stem).with_suffix(".epub")
        else:
            # Get name from input's parent directory
            output = (output / output.stem).with_suffix(".epub")

    # Now we should have valid file, change suffix to epub
    # TODO: maybe not, if output is file with some different suffix, it will be overiden

    # Now, check if file exists
    if output.exists() and not overwrite:
        raise RuntimeError(
            f"Output ePub at path '{output.as_posix()}' already exists! Use `--overwrite` to replace it."
        )

    return output


# region Move it to BookProcessor

# @staticmethod
# def register_page_type(type: str, factory: Type, processor_cls: Type):
#     if not isinstance(processor_cls, Type) or not issubclass(processor_cls, PageProcessor):
#         logger.warning(f"`processor_cls` must inherit from PageProcessor class! '{processor_cls}' given.")
#         return None

#     BookProcessor.page_processors[type] = processor_cls

#     if not isinstance(factory, Type) or not issubclass(factory, BookPage):
#             logger.warning(f"`factory_type` must inherit from BookPage class! '{factory}' given.")
#             return None

#     BookProcessor.page_factories[type] = lambda x: factory(**x)

# @staticmethod
# def register(type: str, factory: callable):
#     BookProcessor.page_factories[type] = factory


# @staticmethod
# def instantiate_page_model(type: str):
#     clbk = BookProcessor.page_factories.get(type)
