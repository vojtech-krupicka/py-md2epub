import uuid
from datetime import UTC, datetime
from typing import Annotated

from pydantic import BaseModel, Field, field_validator, model_validator

from md2epub.models.public import docs
from md2epub.models.public.common import Author, BookId, CalibreMetadata, Contributor, Identifier


class Metadata(BaseModel):
    title: Annotated[str, Field(**docs.metadata_title)]
    """The title of the book."""

    supertitle: Annotated[str, Field(**docs.metadata_supertitle)] = ""
    """The supertitle of the book."""

    subtitle: Annotated[str, Field(**docs.metadata_subtitle)] = ""
    """The subtitle of the book."""

    author: Annotated[Author, Field(default_factory=Author, **docs.metadata_author)]
    """The main author of the book."""

    additional_authors: Annotated[list[Author], Field(**docs.metadata_additional_authors)] = []
    """Additional authors of the book."""

    language: Annotated[str, Field(**docs.metadata_language)] = "en"
    """The language of the book."""

    book_id: Annotated[BookId, Field(default_factory=BookId, **docs.metadata_book_id)]
    """The unique ID of the book."""

    created: Annotated[str | int | None, Field(**docs.metadata_created)] = None
    """The date and time when the book was created. Can be a string or an integer timestamp."""

    published: Annotated[str | int | None, Field(**docs.metadata_published)] = None
    """The date and time when the book was published. Can be a string or an integer timestamp."""

    modified: Annotated[str | int | None, Field(**docs.metadata_modified)] = None
    """The date and time when the book was last modified. Can be a string or an integer timestamp."""

    format: Annotated[str, Field(**docs.metadata_format)] = "application/epub+zip"
    """The file format, physical medium, or dimensions of the resource;
    see https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.9"""

    identifiers: Annotated[list[Identifier], Field(**docs.metadata_identifiers)] = []
    """Identifies as An unambiguous reference to the resource within a given context.
    see: https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.10"""

    subjects: Annotated[list[str], Field(**docs.metadata_subjects)] = []
    """The topic of the resource.
    Typically, the subject will be represented using keywords, key phrases, or classification codes.
    Recommended best practice is to use a controlled vocabulary.
    see: https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.3"""

    description: Annotated[str, Field(**docs.metadata_description)] = ""
    """Description may include but is not limited to: an abstract, a table of contents, a graphical
    representation, or a free-text account of the resource.
    see: https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.4"""

    publisher: Annotated[str, Field(**docs.metadata_publisher)] = ""
    """An entity responsible for making the resource available.
    see: https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.5"""

    contributors: Annotated[list[Contributor], Field(**docs.metadata_contributors)] = []
    """The guidelines for using names of persons or organizations as creators also apply to
    contributors. Typically, the name of a Contributor should be used to indicate the entity.
    see: https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.6"""

    rights: Annotated[list[str], Field(**docs.metadata_rights)] = []
    """Information about rights held in and over the resource.
    see: https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.15"""

    calibre: Annotated[CalibreMetadata, Field(default_factory=CalibreMetadata, **docs.metadata_calibre)]
    """Calibre metadata for sorting and defining book series and book series index."""

    title_separator: Annotated[str, Field(**docs.metadata_title_separator)] = " - "
    """The separator to use between the title and subtitle of the book."""

    @field_validator("supertitle", "title", "subtitle", mode="before")
    @classmethod
    def validate_titles(cls, val):
        # If value set to none from yaml (empty), than change it to empty string
        if val is None:
            return ""

        return val

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

        if not (self.book_id.value or "").strip():
            seed = f"md2epub|{self.title}|{self.author.name}|{self.published}|{self.language}"
            self.book_id.value = str(uuid.uuid5(uuid.NAMESPACE_URL, seed))

        return self
