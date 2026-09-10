from __future__ import annotations

import uuid
from enum import StrEnum, auto
from pathlib import Path
from typing import Any, ClassVar

from pydantic import BaseModel, Field, computed_field, field_validator, model_validator

import md2epub.models.public.common_docs as docs

# region Enums


class PageType(StrEnum):
    Cover = auto()
    Title = auto()
    Toc = auto()
    Chapter = auto()
    Book = auto()
    Custom = auto()
    _Unknown = auto()

    @classmethod
    def _missing_(cls, value):
        return PageType._Unknown


class OpfGuideType(StrEnum):
    Cover = auto()
    TitlePage = "title-page"
    TOC = auto()
    Index = auto()
    LOI = auto()
    LOT = auto()
    Notes = auto()
    Preface = auto()
    Text = auto()


# region Content base model


class BookContent(BaseModel, validate_assignment=True):
    name: str = ""

    supertitle: str = ""
    title: str = ""
    subtitle: str = ""

    stylesheets: set[Path] = []
    stylesheets_overrides: set[Path] = []

    @field_validator("supertitle", "title", "subtitle", mode="before")
    @classmethod
    def validate_titles(cls, val):
        # If value set to none from yaml (empty), than change it to empty string
        if val is None:
            return ""

        return val


# region Page base model


class Page(BookContent, validate_assignment=True):
    TYPE: ClassVar[str]
    DEFAULT_TEMPLATE: ClassVar[Path]

    opf_spine_add: bool = False
    opf_spine_aux: bool = False
    opf_guide_type: OpfGuideType | None = None
    opf_guide_title: str = ""
    add_to_toc: bool = False

    custom_template: Path | None = None

    @computed_field
    @property
    def type(self) -> Path:
        return self.TYPE

    @computed_field
    @property
    def template_path(self) -> Path:
        return self.custom_template if self.custom_template else self.DEFAULT_TEMPLATE


# region Metadata


class Identifier(BaseModel, validate_assignment=True):
    """
    Represents identifier in ePub metadata section.

    Value of the identifier should be unique.
    Scheme is type of identifier (uuid, isbn, ...).

    See: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.10>
    """

    scheme: str = Field("uuid", **docs.identifier_scheme)
    value: str = Field(default_factory=lambda: str(uuid.uuid4()), **docs.identifier_value)


class BookId(Identifier, validate_assignment=True):
    """
    Represents ePub `unique-identifier` in ePub OPF `package` as well as main identifier
    in metadata section.

    See: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.10>
    """

    id: str = Field("BookId", **docs.bookid_id)


class Contributor(BaseModel, validate_assignment=True):
    """
    A party whose contribution to the publication is secondary to those named in creator elements.

    See: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.6>
    """

    role: str = Field("", **docs.contributor_role)
    name: str = Field("Anonymous Entity", **docs.contributor_name)
    file_as: str = Field("", **docs.contributor_file_as)

    @model_validator(mode="after")
    def on_after_model_validate(self):
        # If not set file_as correctly (at all), set it as 'Surname, Name'
        if not self.file_as:
            parts = [part for part in self.name.split(" ") if "." not in part]
            self.file_as = (
                f"{parts[-1]}, {" ".join(parts[:-1])}" if len(parts) > 1 else " ".join(parts)
            )
        return self


class Author(Contributor, validate_assignment=True):
    """
    A author of the publication. It fills `creator` elements in ePub OPF `package` metadata.

    Publications can have multiple co-authors, the order of authors is presumed to define the order in which the creator's names **should** be presented by the Reading System.

    Note: additional contributors whose contributions are secondary to those listed in `creator` elements **should** be named in `contributor` elements.

    See: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.2>
    """

    role: str = "aut"

    @model_validator(mode="before")
    @classmethod
    def on_before_model_validate(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"name": data}

        return data


class CalibreMetadata(BaseModel, validate_assignment=True):
    """
    Calibre metadata for sorting and defining book series and book series index.
    """

    title_sort: str = Field("", **docs.calibre_title_sort)
    series: str = Field("", **docs.calibre_series)
    series_index: int = Field(1, **docs.calibre_series_index)
    author_link_map: str = Field("", **docs.calibre_author_link_map)
