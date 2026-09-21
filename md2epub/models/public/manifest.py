from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Annotated, Any

from pydantic import BaseModel, Field, computed_field, model_validator

from md2epub import __version__
from md2epub.models.public.common import Author, BookId, CalibreMetadata, Contributor, Identifier
from md2epub.models.public.config import Config
from md2epub.models.public.docs import manifest as docs
from md2epub.models.public.page import Book


class Manifest(BaseModel, validate_assignment=True):
    file: Annotated[Path, Field()]
    """The path to the manifest file."""

    title: Annotated[str, Field(**docs.manifest_title)]
    """The title of the book."""

    supertitle: Annotated[str, Field(**docs.manifest_supertitle)] = ""
    """The supertitle of the book."""

    subtitle: Annotated[str, Field(**docs.manifest_subtitle)] = ""
    """The subtitle of the book."""

    author: Annotated[Author, Field(default_factory=Author)]
    """The main author of the book."""

    additional_authors: Annotated[list[Author], Field()] = []
    """Additional authors of the book."""

    language: Annotated[str, Field(**docs.manifest_language)] = "en"
    """The language of the book."""

    created: Annotated[str | int | None, Field(**docs.manifest_created)] = None
    """The date and time when the book was created. Can be a string or an integer timestamp."""

    # region Optional metadata

    book_id: Annotated[BookId, Field(default_factory=BookId)]
    """The unique ID of the book."""

    published: Annotated[str | int | None, Field(**docs.manifest_published)] = None
    """The date and time when the book was published. Can be a string or an integer timestamp."""

    modified: Annotated[str | int | None, Field(**docs.manifest_modified)] = None
    """The date and time when the book was last modified. Can be a string or an integer timestamp."""

    format: Annotated[str, Field()] = "application/epub+zip"
    """The file format, physical medium, or dimensions of the resource; 
    see https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.9"""

    identifiers: Annotated[list[Identifier], Field()] = []
    """Identifies as An unambiguous reference to the resource within a given context.
    see: https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.10"""

    subjects: Annotated[list[str], Field()] = []
    """The topic of the resource.
    Typically, the subject will be represented using keywords, key phrases, or classification codes. 
    Recommended best practice is to use a controlled vocabulary.
    see: https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.3"""

    description: Annotated[str, Field()] = ""
    """Description may include but is not limited to: an abstract, a table of contents, a graphical 
    representation, or a free-text account of the resource.
    see: https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.4"""

    publisher: Annotated[str, Field()] = ""
    """An entity responsible for making the resource available.
    see: https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.5"""

    contributors: Annotated[list[Contributor], Field()] = []
    """The guidelines for using names of persons or organizations as creators also apply to 
    contributors. Typically, the name of a Contributor should be used to indicate the entity.
    see: https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.6"""

    rights: Annotated[list[str], Field()] = []
    """Information about rights held in and over the resource.
    see: https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.15"""

    calibre: Annotated[CalibreMetadata, Field(default_factory=CalibreMetadata)]
    """Calibre metadata for sorting and defining book series and book series index."""

    # region Private and other fields

    book: Annotated[Book, Field()]
    """Book model containing information about the book."""

    config: Annotated[Config, Field(default_factory=Config)]
    """Config model for epub, parser and markdown converter"""

    # region Computed fields and validators

    @computed_field
    @property
    def full_title(self) -> str:
        """Return the full title of the book, including subtitle if present."""
        return f"{self.title} - {self.subtitle}" if self.subtitle else self.title

    @computed_field
    @property
    def version(self) -> str:
        """Return the version of the md2epub package."""
        return __version__

    @model_validator(mode="after")
    def on_after_model_validate(self):
        now = datetime.now(tz=UTC)
        if self.created is None:
            self.created = now.strftime("%Y")
        if self.published is None:
            self.published = now.strftime("%Y-%m-%d")
        if self.modified is None:
            self.modified = now.strftime("%Y-%m-%d")

        if not self.calibre.author_link_map:
            self.calibre.author_link_map = f"{{&quot;{self.author.name}&quot;: &quot;&quot;}}"

        # Set all main info from manifest into the main book element
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
        """Load manifest from file. The file can be in JSON or YAML format."""

        data = {}
        with open(input.as_posix(), "r", encoding=encoding) as ifp:
            if input.suffix.lower() == ".json":
                import json

                data = json.load(ifp)
            elif input.suffix.lower() in (".yaml", ".yml"):
                import yaml

                data = yaml.safe_load(ifp)
            else:
                raise RuntimeError(f"Error: invalid manifest format '{input}'! Valid formats are 'json' or 'yaml'.")

        return Manifest.create(input, data)

    @classmethod
    def load_from_string(cls, text: str, type: str = "yaml") -> Manifest:
        """Load manifest from string. The string can be in JSON or YAML format."""

        data = {}
        if type == "json":
            import json

            data = json.loads(text)
        elif type in ("yaml", "yml"):
            import yaml

            data = yaml.safe_load(text)
        else:
            raise RuntimeError(f"Error: invalid manifest format '{type}'! Valid formats are 'json' or 'yaml'.")

        return Manifest.create(Path(), data)

    @classmethod
    def create(cls, input: Path, data: dict[Any, Any]) -> Manifest:
        """Create manifest from data dictionary. Use input as the file field."""
        return Manifest(file=input, **data)
