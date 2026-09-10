from __future__ import annotations

from pathlib import Path
from typing import Any, Type

import md2epub.utils.utils as Utils
from md2epub.models.public.manifest import Manifest
from md2epub.models.public.pages import (
    BookPart,
    Chapter,
    CoverPage,
    CustomPage,
    PageType,
    TitlePage,
    TocPage,
)
from md2epub.processors.book_processor import BookProcessor
from md2epub.processors.page_processor import (
    BookPartProcessor,
    ChapterPageProcessor,
    CoverPageProcessor,
    CustomPageProcessor,
    TitlePageProcessor,
    TocPageProcessor,
)
from md2epub.utils.page_factory import PageFactory

logger = Utils.get_logger()


class Builder:
    """
    Build ePub from manifest.
    """

    # region Contructor

    def __init__(self, **kwargs):
        """
        :param register_default_processors: (Optional)
        :param book_processor_class: (Optional)
        :param ncx_processor_class: (Optional)
        :param opf_processor_class: (Optional)
        """

        self.manifest: Manifest = None

        # Get processor classes for book, ncx and opf
        self.book_processor_cls: Type = kwargs.get("book_processor_class", BookProcessor)
        self.ncx_processor_cls: Type = kwargs.get("ncx_processor_class")
        self.opf_processor_cls: Type = kwargs.get("opf_processor_class")

        # If register_default_processors set to True, then all default book processors will
        # be registered with all core book page factories
        if kwargs.get("register_default_processors", True):
            self.register_default_processors()

    # region Build ePub

    def build(self, manifest: Manifest, output: Path):
        # Set manifest
        self.manifest = manifest
        assert self.manifest is not None

        logger.info(f"output path: {output}")

    def collect(self):
        pass

    def write(self, output):
        pass

    # region Manifest API

    # region Utilities

    def register_default_processors(self):
        def _create_cover_title_toc_page(data: dict[str, Any]):
            yield TitlePage(**data)
            yield CoverPage(**data)
            yield TocPage(**data)

        BookProcessor.register_page(PageType.Cover, CoverPage, CoverPageProcessor)
        BookProcessor.register_page(PageType.Title, TitlePage, TitlePageProcessor)
        BookProcessor.register_page(PageType.Toc, TocPage, TocPageProcessor)
        BookProcessor.register_page(PageType.Chapter, Chapter, ChapterPageProcessor)
        BookProcessor.register_page(PageType.Custom, CustomPage, CustomPageProcessor)
        BookProcessor.register_page(PageType.Book, BookPart, BookPartProcessor)

        PageFactory.register("cover_title_toc", _create_cover_title_toc_page)

    # region With statement support

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass
