from __future__ import annotations

import codecs
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, computed_field, model_validator

import md2epub.models.public.manifest_docs as docs
from md2epub import __version__

from .book import Book
from .common import Author, BookId, CalibreMetadata, Contributor, Identifier
from .config import Config


class Manifest(BaseModel, validate_assignment=True):
    title: str = Field(**docs.manifest_title)
    subtitle: str = Field("", **docs.manifest_subtitle)
    author: Author = Author()
    additional_authors: list[Author] = []
    language: str = Field("en", **docs.manifest_language)
    created: str | int | None = Field(None, **docs.manifest_created)

    # region Optional metadata

    book_id: BookId = BookId()

    published: str | int | None = Field(None, **docs.manifest_published)
    modified: str | int | None = Field(None, **docs.manifest_modified)

    # The file format, physical medium, or dimensions of the resource.
    # see https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.9
    format: str = "application/epub+zip"

    # Identifies as An unambiguous reference to the resource within a given context.
    # see: https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.10
    identifiers: list[Identifier] = []

    # The topic of the resource.
    # Typically, the subject will be represented using keywords, key phrases, or classification codes. Recommended best practice is to use a controlled vocabulary.
    # see: https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.3
    subjects: list[str] = []

    # Description may include but is not limited to: an abstract, a table of contents, a graphical representation, or a free-text account of the resource.
    # see: https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.4
    description: str = ""

    # An entity responsible for making the resource available.
    # see: https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.5
    publisher: str = ""

    # The guidelines for using names of persons or organizations as creators also apply to contributors. Typically, the name of a Contributor should be used to indicate the entity.
    # see: https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.6
    contributors: list[Contributor] = []

    # Information about rights held in and over the resource.
    # see: https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.15
    rights: list[str] = []

    # Calibre metadata
    calibre: CalibreMetadata = CalibreMetadata()

    # region Private and other fields

    # Config model for epub, parser and markdown conventor
    config: Config = Config()

    # Bookinfo contains info about book
    book: Book = Book()

    # Manifest file as Path
    _file: Path | None = None

    # region Computed fields and validators

    @computed_field
    @property
    def cli_version(self) -> str:
        return __version__

    @computed_field
    @property
    def manifest_version(self) -> str:
        return __version__

    @model_validator(mode="after")
    def on_after_model_validate(self):
        now = datetime.now()
        if self.created is None:
            self.created = now.strftime("%Y")
        if self.published is None:
            self.published = now.strftime("%Y-%m-%d")
        if self.modified is None:
            self.modified = now.strftime("%Y-%m-%d")

        if not self.calibre.author_link_map:
            self.calibre.author_link_map = f"{{&quot;{self.author.file_as}&quot;: &quot;&quot;}}"

        # Set title and subtitle to root book
        self.book.title = self.title
        self.book.subtitle = self.subtitle
        self.book.author = self.author
        self.book.language = self.language
        self.book.created = self.created
        self.book.identifiers = self.identifiers
        self.book.subjects = self.subjects
        self.book.description = self.description
        self.book.publisher = self.publisher
        self.book.contributors = self.contributors
        self.book.rights = self.rights

        return self

    # region Load and create manifest

    @classmethod
    def load_from_file(cls, input: Path, encoding: str = "utf-8") -> Manifest:
        data = {}
        with codecs.open(input.as_posix(), "r", encoding=encoding) as ifp:
            if input.suffix == ".json":
                data = json.load(ifp)
            elif input.suffix in (".yaml", ".yml"):
                data = yaml.safe_load(ifp)
            else:
                raise RuntimeError(
                    f"Error: invalid manifest format '{input}'! Valid formats are 'json' or 'yaml'."
                )

        return Manifest.create(input, data)

    @classmethod
    def load_from_string(cls, text: str, type: str = "yaml") -> Manifest:
        data = {}
        if type == "json":
            data = json.loads(text)
        elif type in ("yaml", "yml"):
            data = yaml.safe_load(text)
        else:
            raise RuntimeError(
                f"Error: invalid manifest format '{type}'! Valid formats are 'json' or 'yaml'."
            )

        return Manifest.create(Path(), data)

    @classmethod
    def create(cls, input: Path, data: dict[Any, Any]) -> Manifest:
        data["_file"] = input
        return Manifest(**data)
