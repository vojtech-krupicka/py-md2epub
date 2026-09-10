from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Type

import md2epub.utils.utils as Utils
from md2epub.models.public.book import Book
from md2epub.models.public.pages import PageType
from md2epub.processors.page_processor import PageProcessor
from md2epub.processors.processor import ContentProcessor
from md2epub.utils.page_factory import PageFactory

if TYPE_CHECKING:
    from md2epub.builder import Builder

logger = Utils.get_logger()


# region BookProcessor


class BookProcessor(ContentProcessor[Book]):
    """ """

    page_processors: ClassVar[dict[str, Type]] = {}

    # region Contructor

    def __init__(self, builder: Builder, model: Book, parent: BookProcessor | None = None):
        super().__init__(builder, model, parent)

        # self.model: Book = model
        # self.parent: BookProcessor | None = parent
        self.level: int = parent.level + 1 if parent else 0

        # self.toc: Toc = Toc()
        # self.pages: OrderedDict[str, list[PageItem]] = OrderedDict()

        # self.resolve_metadata()

    # region Page processors

    @staticmethod
    def register_page(
        type: str | PageType, page_factory: Type | callable | None, processor_cls: Type
    ):
        # If page factory is not given (is None or False), skip factory registration.
        if page_factory is not None:
            # We will use original page type
            PageFactory.register(type, page_factory)

        # Check processor class
        if not isinstance(processor_cls, Type) and issubclass(processor_cls, PageProcessor):
            logger.warning(
                f"`processor_cls` must inherit from PageProcessor class! '{processor_cls}' given."
            )
            return

        # Type can be sting or type from PageType enum
        type = type.value if isinstance(type, PageType) else str(type)

        # If type is already registered, show warning
        if type in BookProcessor.page_processors:
            cls = BookProcessor.page_processors[type]
            logger.warning(
                f"Page processor for '{type}' page is already registered with '{cls.__name__}'!"
            )

        # Register processor
        BookProcessor.page_processors[type] = processor_cls

    @staticmethod
    def deregister(type: str | PageType):
        # Type can be sting or type from PageType enum
        type = type.value if isinstance(type, PageType) else str(type)

        # If type is already registered, show warning
        if type not in BookProcessor.page_processors:
            logger.warning(f"Page processor for '{type}' page was never registered!")
            return

        return BookProcessor.page_processors.pop(type)

    @staticmethod
    def clear():
        BookProcessor.page_processors.clear()
