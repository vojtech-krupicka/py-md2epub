from __future__ import annotations

import logging
import sys
from functools import partial, wraps
from pathlib import Path

import click

from md2epub import __appname__, __pgkdir__, __python_version__, __version__
from md2epub.core.environment import setup_environment
from md2epub.utils.exceptions import catch_exception
from md2epub.utils.timing import timing

# Defaults
defaul_log_cfg_path = Path(__file__) / "../conf/logging.yaml"
default_log_level = logging.INFO

# region Click default options


def add_options(*opts):
    def inner(f):
        for i in reversed(opts):
            f = i(f)
        return f

    return inner


def verbose_option(f):
    def callback(ctx, param, value):
        if value:
            return logging.DEBUG

    return click.option(
        "-v",
        "--verbose",
        is_flag=True,
        help="Enable verbose output (i.e. DEBUG).",
        callback=callback,
    )(f)


def quiet_option(f):
    def callback(ctx, param, value):
        if value:
            return logging.CRITICAL

    return click.option(
        "-q",
        "--quiet",
        is_flag=True,
        help="Silence warnings.",
        callback=callback,
    )(f)


def log_cfg_path_option(f):
    log_cfg_path_type = click.Path(exists=True, writable=False, resolve_path=True, path_type=Path)
    return click.option(
        "--log-cfg-path",
        type=log_cfg_path_type,
        default=defaul_log_cfg_path.as_posix(),
        metavar="LOG_CONF_FILE",
        envvar="MD2EPUB_LOG_CONF_FILE",
        help=f"Path to the logging config file in YAML format (default '{defaul_log_cfg_path}').",
    )(f)


# region Cli group

context_settings = {"help_option_names": ["-h", "--help"], "max_content_width": 120}
version_msg = f"{__appname__}, version {__version__} from {__pgkdir__} (Python {__python_version__})"
common_options = add_options(
    quiet_option,
    verbose_option,
    log_cfg_path_option,
)


@click.group(context_settings=context_settings)
@click.version_option(__version__, "-V", "--version", message=version_msg)
def cli():
    """Md2ePub - Create ePubs easily from Markdown files."""


# region Commands


def md2epub_command(func=None, *gargs, **gkwargs):
    if not func:
        return partial(md2epub_command, *gargs, **gkwargs)

    @wraps(func)
    def wrapper(*args, **kwargs):
        def parse_cmd_name():
            return func.__name__.removesuffix("_command").replace("_", "-")

        args += gargs
        kwargs.update(gkwargs)

        # Parse command name from func name if not set, strip `_command` from its end and replace `_` to `-`
        cmd_name = kwargs.pop("cmd_name", parse_cmd_name())
        log_cfg_path = kwargs.pop("log_cfg_path", defaul_log_cfg_path)
        log_level = kwargs.pop("quiet", None) or kwargs.pop("verbose", None) or default_log_level

        # Setup and get get environment
        appname = f"{__appname__}-{cmd_name}"
        env = setup_environment(appname, version=__version__)
        env.setup_logger(
            log_cfg_path,
            name=appname,
            logging_level=log_level,
        )

        try:
            # Run command
            env.logger.info(f"Running command '{cmd_name}' ...")

            with timing() as t:
                func(*args, **kwargs)

            env.logger.info(f"Command '{cmd_name}' finished successfully in {t}.")
        except Exception:
            env.logger.exception(f"Error in '{cmd_name}' command!")
            sys.exit(1)

    return wrapper


# region Build command

overwrite_option = click.option(
    "--overwrite",
    is_flag=True,
    default=False,
    help="Overwrite existing EPUB_FILE",
)

input_manifest_argument = click.argument(
    "input-manifest",
    type=click.Path(exists=True, resolve_path=True, path_type=Path),
    default=None,
    metavar="MANIFEST",
    envvar="MD2EPUB_MANIFEST_ARGUMENT",
    help="Path to the input manifest file.",
)

output_epub_argument = click.argument(
    "output-epub",
    type=click.Path(exists=False, writable=True, resolve_path=True, path_type=Path),
    default=None,
    required=False,
    metavar="EPUB_FILE",
    envvar="MD2EPUB_EPUB_ARGUMENT",
    help="Path to the output EPUB file.",
)


@cli.command(name="build")
@common_options
@input_manifest_argument
@output_epub_argument
@overwrite_option
@catch_exception(handle=(Exception))
@md2epub_command()
def build_command(
    input_manifest: Path | None = None,
    output_epub: Path | None = None,
    overwrite: bool = False,
):
    """
    Build ePub from input MANIFEST file into output EPUB_FILE.

    MANIFEST can be in YAML (`.yml`, `.yaml`) or JSON (`.json`) format file or valid directory.
    According to the type of MANIFEST, the following behaviour is expected:
        - if MANIFEST is a valid file, then this file will be read as input configuration and its
            parent folder will be set as `work_dir`.
        - if MANIFEST is a valid directory, then within this directory one of the following files
            will be searched: `manifest.yml`, `manifest.yaml`, `manifest.json`. Then the MANIFEST
            directory will be set as `work_dir`.
        - if MANIFEST is None, then the current directory will be set as valid directory and the
            same behaviour as above is expected.

    EPUB_FILE is the output, which can be set to:
        - valid file, then this file is the output,
        - valid directory, then name of the directory is output file name with `.epub` extension,
        - None, then first, MANIFEST name is checked and if its not default `manifest` name, then
            this name will be used, else, name of the parent directory is used with `.epub` extension.

    Correct extension of the output EPUB_FILE will be automatically added if not specified. It can
    overriden by specifying custom output extension in the MANIFEST file under
    `config.md2epub.epub_suffix` key.

    If the resolved output EPUB_FILE already exists, it will be overwritten only if the
    `--overwrite` option is specified, otherwise an error will be raised.
    """

    from md2epub.commands import build

    return build.run(input_manifest, output_epub, overwrite)


@cli.command(name="create")
@common_options
@md2epub_command()
def create_command(**kwargs):
    # from md2epub.commands import create

    # return create.run(**kwargs)
    print("Creating...")


@cli.command(name="schema")
@common_options
@md2epub_command()
def schema_command(**kwargs):
    # from md2epub.commands import schema

    # return schema.run(**kwargs)
    print("Generating schema...")


if __name__ == "__main__":
    cli()
