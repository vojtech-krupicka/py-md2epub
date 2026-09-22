from __future__ import annotations

from collections import OrderedDict
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

from pydantic import BaseModel

from md2epub.core.content_collector import ContentCollector
from md2epub.models.public.page import Book, Page, PageType, TocPage
from md2epub.models.toc import Toc, TocItem
from md2epub.processors.content_processor import ContentProcessor, HtmlInlineFile
from md2epub.types.epub_content import HtmlFile
from md2epub.utils.filters import toc_href_filter
from md2epub.utils.utils import xml_id

if TYPE_CHECKING:
    from md2epub.processors.page_processor import PageProcessor


class PageItem(BaseModel):
    source: Path
    model: Page
    html_file: HtmlFile


class BookProcessor(ContentProcessor[Book]):
    PAGE_PROCESSORS: ClassVar[dict[PageType, type[PageProcessor]]] = {}

    def __init__(self, collector: ContentCollector, parent: BookProcessor | None, model: Book):
        super().__init__(collector, parent, model)

        self.parent: BookProcessor | None = parent
        self.level = parent.level + 1 if parent else 0

        self.toc = Toc()
        self.pages: OrderedDict[PageType, list[PageItem]] = OrderedDict()

        self.resolve_metadata()

    @classmethod
    def register_page_processor(cls, page_type: PageType, processor_cls: type[PageProcessor]):
        from md2epub.processors.page_processor import PageProcessor

        if not isinstance(processor_cls, type) and issubclass(processor_cls, PageProcessor):
            raise TypeError(
                f"Cannot register page processor for '{page_type}' to '{processor_cls}'! processor_cls must inherit from PageProcessor class."
            )

        cls.PAGE_PROCESSORS[page_type] = processor_cls

    @property
    def is_root(self) -> bool:
        return self.parent is None

    def add_page(self, source: Path, model: Page, html_file: HtmlFile):
        item = PageItem(source=source, model=model, html_file=html_file)
        self.pages.setdefault(model.type, []).append(item)

    def resolve_metadata(self):
        if self.parent is None:
            return

        if not self.model.author:
            self.model.author = self.parent.model.author
        if not self.model.language:
            self.model.language = self.parent.model.language
        if not self.model.created:
            self.model.created = self.parent.model.created
        if not self.model.identifiers:
            self.model.identifiers = self.parent.model.identifiers
        if not self.model.subjects:
            self.model.subjects = self.parent.model.subjects
        if not self.model.description:
            self.model.description = self.parent.model.description
        if not self.model.publisher:
            self.model.publisher = self.parent.model.publisher
        if not self.model.contributors:
            self.model.contributors = self.parent.model.contributors
        if not self.model.rights:
            self.model.rights = self.parent.model.rights

    def run(self):
        # First, get styles from parent
        self.resolve_styles()

        # Than collect all files
        self.collect_files(list(self.model.files))

        # Finally, process content
        for page in self.model.pages:
            cls = self.PAGE_PROCESSORS.get(page.type)
            if not cls:
                raise RuntimeError(f"Cannot process page '{page.type.value}'! Page processor not found.")

            pp = cls(self.collector, self, page)
            pp.run()

        # Render TOC for current book
        self.render_toc()

        # If this book is not root, add its TOC to the parent. `render_toc()` above already guarantees
        # `self.toc.file` is set (it raises otherwise), so this heading can link to the sub-book's own
        # table of contents instead of being a dead `href=""`.
        toc_title = self.model.toc_title or self.model.title
        if self.parent is not None:
            self.parent.add_toc_page(
                {
                    "level": self.level,
                    "id": xml_id(self.model.name),
                    "name": toc_title,
                    "html": toc_title,
                    "source": self.toc.file.source if self.toc.file else "",
                    "children": self.toc.children,
                }
            )

    def set_toc(self, file: HtmlFile, model: TocPage, stylesheets: list[HtmlInlineFile]):
        if self.toc.is_set:
            self.env.logger.warning(f"TOC for book '{self.model.title}' already set! Skipping...")
            return

        self.toc.is_set = True
        self.toc.file = file
        self.toc.page = model
        self.toc.stylesheets = stylesheets

    def add_toc_page(self, data: dict[str, Any]):
        item = TocItem(**data)
        self.toc.children.append(item)

    def render_toc(self):
        if not self.toc.file or not self.toc.page:
            raise RuntimeError("Cannot render TOC for this Book, TOC has not been set yet!")

        self.toc.file.content = self.render(
            self.toc.page.template_path,
            filters={"href": toc_href_filter},
            book=self.model,
            stylesheets=self.toc.stylesheets,
            model=self.toc.page,
            toc=self.toc,
        )
