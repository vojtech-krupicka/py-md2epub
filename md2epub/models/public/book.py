from __future__ import annotations

import re
from enum import StrEnum, auto
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Type

from pydantic import BaseModel, Field, computed_field, field_validator, model_validator

import md2epub.models.public.book_docs as docs
import md2epub.utils.utils as Utils
from md2epub import current_config as config
from md2epub.models.public.common import Author, BookContent, Contributor, Identifier, Page
from md2epub.utils.page_factory import PageFactory

# Get default logger
logger = Utils.get_logger()

# region Book model


class Book(BookContent, validate_assignment=True):
    # Book identifier
    name: str = "book"

    # Book metadata
    author: Author = Author()
    language: str = ""
    created: str | int | None = None
    identifiers: list[Identifier] = []
    subjects: list[str] = []
    description: str = ""
    publisher: str = ""
    contributors: list[Contributor] = []
    rights: list[str] = []

    # Additional book settings
    title_separator: str = " - "

    # All files and folders needed by this book
    files: set[Path] = []

    # List of pages in order to render in ePub
    pages: list[Page] = []

    # Computed fields

    @computed_field
    @property
    def full_title(self) -> str:
        return f"{self.title}{self.title_separator}{self.subtitle}" if self.subtitle else self.title

    @field_validator("pages", mode="before")
    @classmethod
    def validate_pages(cls, val):
        assert isinstance(val, list)
        assert len(val) > 0

        pages: list[Page] = []

        for data in val:
            for page in PageFactory.instantiate(data):
                pages.append(page)

        return pages
