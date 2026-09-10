from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, Generic, TypeVar

import md2epub.utils.utils as Utils
from md2epub import current_config as config
from md2epub.models.public.book import BookContent
from md2epub.utils.template import FileTemplate

if TYPE_CHECKING:
    from md2epub.builder import Builder
    from md2epub.processors.book_processor import BookProcessor

logger = Utils.get_logger()


# region Processor


class Processor:
    """
    Base processor.
    """

    def __init__(self, builder: Builder):
        self.builder: Builder = builder

    def run(self, **kwargs: dict[str, Any]):
        raise NotImplementedError("This is not implemented!")

    def render(self, tpl: Path, filters: dict[str, callable] | None = None, **data: dict[str, Any]):
        template = FileTemplate(tpl, filters=filters)
        content = template.render(**data)
        if not content:
            raise RuntimeWarning(f"Cannot render template '{tpl}'!")

        return content


# region ContentProcessor

T_Content = TypeVar("T", bound=BookContent)


class ContentProcessor(Processor, Generic[T_Content]):
    """
    Base generic class for all content processors (book and pages).
    """

    def __init__(self, builder: Builder, model: T_Content, parent: BookProcessor | None = None):
        super().__init__(builder)

        self.model: T_Content = model
        self.parent: BookProcessor = parent
        self.collected_styles: list[str] = []
