from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel

from md2epub.models.public.page import TocPage
from md2epub.types.epub_content import HtmlFile


class TocItem(BaseModel):
    source: Path | None = None
    level: int
    id: str
    name: str
    html: str
    children: list[TocItem] = []


class Toc(BaseModel):
    file: HtmlFile | None = None
    page: TocPage | None = None
    stylesheets: list = []
    children: list[TocItem] = []
    is_set: bool = False
