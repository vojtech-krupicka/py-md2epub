import abc
from collections.abc import Callable
from pathlib import Path

from md2epub.core.content_collector import ContentCollector
from md2epub.core.environment import get_environment
from md2epub.utils.templator import FileTemplator


class Processor(abc.ABC):
    def __init__(self, collector: ContentCollector):
        self.env = get_environment()
        self.collector = collector

    @abc.abstractmethod
    def run(self):
        """Abstract method to override."""
        raise NotImplementedError("This is not implemented!")

    def render(self, tpl: Path, *, filters: dict[str, Callable] | None = None, **data):
        template = FileTemplator(tpl, filters=filters)
        content = template.render(**data)
        if not content:
            raise RuntimeWarning(f"Cannot render template '{tpl}'!")

        return content
