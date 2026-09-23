from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, computed_field, model_validator

from md2epub.models.public.docs import config as docs


class EpubConfig(BaseModel, validate_assignment=True):
    """Application configuration for the Md2ePub from Manifest file."""

    epub_suffix: Annotated[Literal[".epub", ".zip"], Field(**docs.epub_suffix)] = ".epub"
    """The suffix for the output EPUB file."""

    html_suffix: Annotated[str, Field(**docs.html_suffix)] = ".xhtml"
    """The extension for the HTML files."""

    folders: Annotated[list[Path], Field(**docs.epub_folders)] = []
    """List of folders to include in the EPUB."""

    files: Annotated[list[Path], Field(**docs.epub_files)] = []
    """List of files to include in the EPUB."""


class ParserConfig(BaseModel, validate_assignment=True):
    foo: Annotated[str, Field(**docs.parser_placeholder)] = "bar"
    """Placeholder - no parser-level configuration exists yet."""


DEFAULT_EXTENSIONS = [
    "attr_list",
    "fenced_code",
    "smarty",
    "tables",
    # "md2epub.extensions.deflist",
    # "md2epub.extensions.textbox",
    # "md2epub.extensions.footnotes",
    # "md2epub.extensions.translate",
    "md2epub.extensions.vlna",
]

DEFAULT_EXTENSION_CONFIGS = {
    "smarty": {
        "smart_angled_quotes": True,
        "substitutions": {
            "left-single-quote": "&sbquo;",
            "right-single-quote": "&lsquo;",
            "left-double-quote": "&bdquo;",
            "right-double-quote": "&ldquo;",
        },
    }
}


class MarkdownConfig(BaseModel, validate_assignment=True):
    """Configuration for the Markdown parser."""

    tab_length: Annotated[int, Field(**docs.tab_length)] = 4
    """The length of tabs in the Markdown source."""

    output_format: Annotated[Literal["html", "xhtml"], Field(**docs.output_format)] = "xhtml"
    """The output format of the Markdown parser. Can be either 'html' or 'xhtml'."""

    additional_extensions: Annotated[list[str], Field(**docs.additional_extensions)] = []
    """Additional extensions to use with the Markdown parser along with the default ones."""

    extensions_override: Annotated[list[str], Field(**docs.extensions_override)] = []
    """Override the default extensions with these extensions for the Markdown parser."""

    extension_configs: Annotated[dict[str, Any], Field(**docs.extension_configs)] = DEFAULT_EXTENSION_CONFIGS
    """The configuration for the extensions used with the Markdown parser."""

    @computed_field
    @property
    def extensions(self) -> list[str]:
        """Return the list of extensions to use with the Markdown parser."""
        return self.extensions_override or DEFAULT_EXTENSIONS + self.additional_extensions


class Config(BaseModel, validate_assignment=True):
    """The configuration for the md2epub application within Manifest file."""

    include_file: Annotated[Path | None, Field(**docs.include_file)] = None
    """Optional config file from which to include additional configuration.
    This can be a YAML or JSON file."""

    includes_files: Annotated[list[Path], Field(**docs.includes_files)] = []
    """List of config files to included in this config."""

    epub: Annotated[EpubConfig, Field(**docs.config_epub)] = EpubConfig()
    """Basic configuration of ePub"""

    parser: Annotated[ParserConfig, Field(**docs.config_parser)] = ParserConfig()
    """Basic configuration for parser from MD to HTML"""

    markdown: Annotated[MarkdownConfig, Field(**docs.config_markdown)] = MarkdownConfig()
    """Basic configuration of Markdown library"""

    @model_validator(mode="before")
    @classmethod
    def on_before_model_validate(cls, data: Any) -> Any:
        # If include_file is valid, try to load it as a parent Config.
        if include_file := data.get("include_file"):
            include_file = Path(include_file)
            if not include_file.exists() or not include_file.is_file():
                raise ValueError(f"Invalid include file: '{include_file}' does not exist or is not a file.")

            # Load the included config file and merge it with the current data.
            included_config = Config.load_from_file(include_file)

            # Merge included config with current data, giving precedence to current data.
            merged_data = included_config.model_dump()
            merged_data.update(data)

            merged_data["include_file"] = include_file  # Keep the include_file in the merged data
            merged_data["includes_files"].append(include_file)  # Keep track of included files

            return merged_data

        # If include_file is not set, just return the data as is.
        return data

    @classmethod
    def load_from_file(cls, input: Path, encoding: str = "utf-8") -> Config:
        """Load manifest from file. The file can be in JSON or YAML format."""

        data = {}
        with open(input.as_posix(), "r", encoding=encoding) as ifp:
            if input.suffix == ".json":
                import json

                data = json.load(ifp)
            elif input.suffix in (".yaml", ".yml"):
                import yaml

                data = yaml.safe_load(ifp)
            else:
                raise RuntimeError(f"Error: invalid manifest format '{input}'! Valid formats are 'json' or 'yaml'.")

        return Config(**data)
