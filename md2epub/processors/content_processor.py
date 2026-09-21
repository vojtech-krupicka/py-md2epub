from __future__ import annotations

import abc
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from md2epub.core.content_collector import ContentCollector
from md2epub.models.public.page import BookContent
from md2epub.processors import Processor
from md2epub.types.epub_content import EpubFile
from md2epub.utils.utils import safe_join

TModel = TypeVar("TModel")


class HtmlInlineFile(BaseModel):
    uid: str
    href: str
    mimetype: str
    alt: str = ""
    title: str = ""


class ContentProcessor[TModel: BookContent](Processor, abc.ABC):
    def __init__(self, collector: ContentCollector, parent: ContentProcessor | None, model: TModel):
        super().__init__(collector)

        self.model = model
        self.parent = parent
        self.collected_styles: list[EpubFile] = []

    def get_parents(self) -> list[ContentProcessor]:
        if not self.parent:
            return []

        result = [self.parent]
        while parent := self.parent.parent:
            result.append(parent)

        return result

    def resolve_styles(self):
        if self.model.stylesheets_overrides:
            self.collected_styles = self.collect_files(list(self.model.stylesheets_overrides))
        else:
            if self.parent:
                self.collected_styles = [s for s in self.parent.collected_styles]

            self.collected_styles += self.collect_files(list(self.model.stylesheets))

    def collect_files(self, files: list[Path]) -> list[EpubFile]:
        result: list[EpubFile] = []

        for path in files:
            full_path = safe_join(self.env.work_dir, path)
            if not full_path.exists():
                self.env.logger.warning(f"File or folder '{path}' not found! Skipping...")
                continue

            if full_path.is_dir():
                folder_content = [p for p in full_path.iterdir()]
                result += self.collect_files(folder_content)
            else:
                file = EpubFile.create_from_source(full_path)
                self.collector.add_file(file)
                result.append(file)

        return result
