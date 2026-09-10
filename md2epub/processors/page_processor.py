from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar

import md2epub.utils.utils as Utils
from md2epub.models.public.pages import (
    BookPart,
    Chapter,
    CoverPage,
    CustomPage,
    Page,
    TitlePage,
    TocPage,
)
from md2epub.processors.processor import ContentProcessor

if TYPE_CHECKING:
    from md2epub.builder import Builder
    from md2epub.processors.book_processor import BookProcessor

__all__ = [
    "PageProcessor",
    "CoverPageProcessor",
    "TitlePageProcessor",
    "TocPageProcessor",
    "ChapterPageProcessor",
    "CustomPageProcessor",
    "BookPartProcessor",
]

logger = Utils.get_logger()


# region PageProcessor

T_Page = TypeVar("T_Page", bound=Page)


class PageProcessor(ContentProcessor[T_Page]):
    def __init__(self, builder: Builder, model: T_Page, parent: BookProcessor):
        super().__init__(builder, model, parent)

        self.toc: list = []


# region CoverPageProcessor


class CoverPageProcessor(PageProcessor[CoverPage]):
    def run(self):
        pass


# region TitlePageProcessor


class TitlePageProcessor(PageProcessor[TitlePage]):
    def run(self):
        pass


# region TocPageProcessor


class TocPageProcessor(PageProcessor[TocPage]):
    def run(self):
        pass


# region ChapterPageProcessor


class ChapterPageProcessor(PageProcessor[Chapter]):
    def run(self):
        pass


# region CustomPageProcessor


class CustomPageProcessor(PageProcessor[CustomPage]):
    def run(self):
        pass


# region BookPartProcessor


class BookPartProcessor(PageProcessor[BookPart]):
    def run(self):
        pass
