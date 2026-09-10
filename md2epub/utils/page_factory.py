# from __future__ import annotations

import re
from typing import Any, ClassVar, Type

import md2epub.utils.utils as Utils
from md2epub.models.public.common import Page, PageType

# Get default logger
logger = Utils.get_logger()


class PageFactory:
    """ """

    factories: ClassVar[dict[str, Type | callable]] = {}

    # region Instantiate

    @staticmethod
    def instantiate(data: str | dict[str, Any]):
        # Allow string values in pages definition as chapter source
        if isinstance(data, str):
            data = {"type": "chapter", "source": data}

        # If type is missing, assume chapter
        type = data.pop("type", "chapter")

        # If type is not recognized, it will fallback to `_Unknown`
        page_type = PageType(type)
        if page_type == PageType._Unknown:
            # Page type is not recognized, it can be:
            # - a multipage special format
            # - or user defined page type
            return PageFactory._handle_unknown_type(type, data)
        else:
            # Page type is known from PageType enum
            return PageFactory._handle_common_type(type, data)

    def _handle_common_type(type: str, data: dict[str, Any]):
        # Look for factory in factories
        factory = PageFactory.factories.get(type, None)
        if not factory:
            raise RuntimeError(f"Cannot instantiate page with type '{type}', factory is missing!")

        # Just call factory
        return factory(data)

    def _handle_unknown_type(type: str, data: dict[str, Any]):
        # First, check if can be split to multipage
        #
        # Multipage format is: `cover,title,toc` or `cover title toc` or `cover|title|toc`
        # All above will result as ["cover", "title", "toc"]
        #
        # This will keep correct names as sigle world:
        # `chapter` -> ["chapter"] or `user_page` -> ["user_page"]
        subtypes = list(filter(None, re.split(r",|\s+|\|", type)))

        # Now for every subtype call _handle_common_type
        for t in subtypes:
            return PageFactory._handle_common_type(t, data)

    # region Registration

    @staticmethod
    def register(type: str | PageType, page_factory: Type | callable):
        # Type can be sting or type from PageType enum
        type = type.value if isinstance(type, PageType) else str(type)

        # If type is already registered, show warning
        if type in PageFactory.factories:
            logger.warning(f"Page factory for '{type}' page is already registered!")

        # Page factory can be concrete Page type or be callable with
        # signature (dict(str, Any)) -> yield Page.
        if isinstance(page_factory, Type):
            if not issubclass(page_factory, Page):
                logger.warning(
                    f"`page_factory` must inherit from Page class! '{page_factory}' given."
                )
                return

            cls = page_factory

            def _default_factory(data: dict[str, Any]):
                yield cls(**data)

            page_factory = _default_factory

        # Register factory (Type of callable)
        PageFactory.factories[type] = page_factory

    @staticmethod
    def deregister(type: str | PageType):
        # Type can be sting or type from PageType enum
        type = type.value if isinstance(type, PageType) else str(type)

        # If type is already registered, show warning
        if type not in PageFactory.factories:
            logger.warning(f"Page factory for '{type}' page was never registered!")
            return

        return PageFactory.factories.pop(type)

    @staticmethod
    def clear():
        PageFactory.factories.clear()
