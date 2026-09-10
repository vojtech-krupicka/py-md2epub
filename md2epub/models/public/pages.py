from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any

from pydantic import Field, computed_field, field_validator, model_validator

import md2epub.models.public.pages_docs as docs
import md2epub.utils.utils as Utils
from md2epub import current_config as config
from md2epub.models.public.book import Book
from md2epub.models.public.common import OpfGuideType, Page, PageType

__all__ = [
    "CoverPage",
    "TitlePage",
    "TocPage",
    "Chapter",
    "CustomPage",
    "BookPart",
]

# Get default logger
logger = Utils.get_logger()


class CoverPage(Page, validate_assignment=True):
    TYPE: str = PageType.Cover.value
    DEFAULT_TEMPLATE: Path = config.TEMPLATE_DIR / "cover.xhtml.jinja"

    name: str = "cover"
    opf_spine_add: bool = True
    opf_guide_type: OpfGuideType = OpfGuideType.Cover
    opf_guide_title: str = "Cover"

    cover_image: Path = Path("images/cover.jpg")


class TitlePage(Page, validate_assignment=True):
    TYPE: str = PageType.Title.value
    DEFAULT_TEMPLATE: Path = config.TEMPLATE_DIR / "title.xhtml.jinja"

    name: str = "title"
    opf_spine_add: bool = True
    opf_guide_type: OpfGuideType = OpfGuideType.TitlePage
    opf_guide_title: str = "Title"

    images: list[Path] = []
    render_title: bool = True
    render_metadata: bool = True
    additional_content: Path | None = None


class TocPage(Page, validate_assignment=True):
    TYPE: str = PageType.Toc.value
    DEFAULT_TEMPLATE: Path = config.TEMPLATE_DIR / "toc.xhtml.jinja"

    name: str = "toc"
    opf_spine_add: bool = True
    opf_guide_type: OpfGuideType = OpfGuideType.TOC
    opf_guide_title: str = "Table of Contents"

    title: str = "Table of Contents"
    render_links: bool = True
    render_depth: int = 2


class Chapter(Page, validate_assignment=True):
    TYPE: str = PageType.Chapter.value
    DEFAULT_TEMPLATE: Path = config.TEMPLATE_DIR / "chapter.xhtml.jinja"

    name: str = "chapter"
    opf_spine_add: bool = True
    add_to_toc: bool = True

    sequence: str | None = "default"
    source: Path


class CustomPage(Page, validate_assignment=True):
    TYPE: str = PageType.Custom.value
    DEFAULT_TEMPLATE: None = None

    name: str = "custom"

    template: Path
    sources: dict[str, Path] = []
    values: dict[Any, Any] = {}

    @computed_field
    @property
    def template_path(self) -> Path:
        return self.template


class BookPart(Page, validate_assignment=True):
    TYPE: str = PageType.Book.value
    DEFAULT_TEMPLATE: None = None

    name: str = "part"

    book: Book = None

    @computed_field
    @property
    def template_path(self) -> None:
        return None
