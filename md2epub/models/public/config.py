from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field, computed_field, model_validator

from md2epub.core.environment import get_environment
from md2epub.models.public import docs
from md2epub.utils.utils import safe_join

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

    included_files: Annotated[list[Path], Field(**docs.included_files)] = []
    """List of config files to included in this config."""

    markdown: Annotated[MarkdownConfig, Field(**docs.config_markdown)] = MarkdownConfig()
    """Basic configuration of Markdown library"""

    @model_validator(mode="before")
    @classmethod
    def on_before_model_validate(cls, data: Any) -> Any:
        # If include_file is valid, try to load it as a parent Config.
        if include_file := data.get("include_file"):
            include_file = safe_join(get_environment().work_dir, include_file)
            if not include_file.exists() or not include_file.is_file():
                raise ValueError(f"Invalid include file: '{include_file}' does not exist or is not a file.")

            # Load the included config file and merge it with the current data.
            included_config = Config.load_from_file(include_file)

            # Merge included config with current data, giving precedence to current data.
            merged_data = included_config.model_dump()
            merged_data.update(data)

            merged_data["include_file"] = include_file  # Keep the include_file in the merged data
            merged_data["included_files"].append(include_file)  # Keep track of included files

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
