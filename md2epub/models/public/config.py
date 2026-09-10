from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel

# import md2epub.models.public.config_docs as docs


class EpubConfig(BaseModel, validate_assignment=True):
    pass


class ParserConfig(BaseModel, validate_assignment=True):
    pass


class MarkdownConfig(BaseModel, validate_assignment=True):
    tab_length: int = 4
    output_format: Literal["html", "xhtml"] = "xhtml"

    extensions: list[str] = [
        "attr_list",
        "fenced_code",
        "smarty",
        "tables",
        "md.extensions.deflist",
        "md.extensions.textbox",
        "md.extensions.footnotes",
        "md.extensions.translate",
        "md.extensions.vlna",
    ]

    extension_configs: dict[str, Any] = {
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


class Config(BaseModel, validate_assignment=True):
    # Basic configuration of ePub
    epub: EpubConfig = EpubConfig()

    # Bacis configuration for parser from MD to HTML
    parser: ParserConfig = ParserConfig()

    # Bacis configuration of Markdown library
    markdown: MarkdownConfig = MarkdownConfig()
