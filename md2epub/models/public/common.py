from __future__ import annotations

import uuid
from typing import Annotated, Any

from pydantic import BaseModel, Field, model_validator

from md2epub.models.public.docs import common as docs

# region Metadata


class Identifier(BaseModel, validate_assignment=True):
    """
    Represents identifier in ePub metadata section.

    Value of the identifier should be unique.
    Scheme is type of identifier (uuid, isbn, ...).

    See: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.10>
    """

    scheme: Annotated[str, Field("uuid", **docs.identifier_scheme)] = "uuid"
    """The scheme attribute names the system or authority that generated or assigned the text 
    contained within the identifier element, for example `ISBN` or `DOI`. The values of the scheme 
    attribute are case sensitive only when the particular scheme requires it."""

    value: str = Field(default_factory=lambda: str(uuid.uuid4()), **docs.identifier_value)
    """The value of the identifier should be unique. It can be a UUID, ISBN, DOI, or any other 
    unique string."""


class BookId(Identifier, validate_assignment=True):
    """
    Represents ePub `unique-identifier` in ePub OPF `package` as well as main identifier
    in metadata section.

    See: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.10>
    """

    id: Annotated[str, Field("BookId", **docs.bookid_id)] = "BookId"
    """The unique ID of the book."""


class Contributor(BaseModel, validate_assignment=True):
    """
    A party whose contribution to the publication is secondary to those named in creator elements.

    See: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.6>
    """

    role: Annotated[str, Field(**docs.contributor_role)] = ""
    """Role of the author, for example `aut` for author, `edt` for editor, `ill` for illustrator, etc."""

    name: Annotated[str, Field(**docs.contributor_name)] = "Anonymous Entity"
    """Contributor's full name."""

    file_as: Annotated[str, Field(**docs.contributor_file_as)] = ""
    """Normalized form of the contributor's name, for example `Surname, Name`."""

    @model_validator(mode="after")
    def on_after_model_validate(self):
        """If file_as is not set correctly (or at all), set it as 'Surname, Name'"""
        if not self.file_as:
            parts = [part for part in self.name.split(" ") if "." not in part]
            self.file_as = f"{parts[-1]}, {' '.join(parts[:-1])}" if len(parts) > 1 else " ".join(parts)

        return self


class Author(Contributor, validate_assignment=True):
    """
    A author of the publication. It fills `creator` elements in ePub OPF `package` metadata.

    Publications can have multiple co-authors, the order of authors is presumed to define the order in which the creator's names **should** be presented by the Reading System.

    Note: additional contributors whose contributions are secondary to those listed in `creator` elements **should** be named in `contributor` elements.

    See: <https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm#Section2.2.2>
    """

    role: Annotated[str, Field(**docs.contributor_role)] = "aut"
    """Role of the author, here already set to `aut` for author, as this is the main author of the book."""

    @model_validator(mode="before")
    @classmethod
    def on_before_model_validate(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {"name": data}

        return data


class CalibreMetadata(BaseModel, validate_assignment=True):
    """Calibre metadata for sorting and defining book series and book series index."""

    title_sort: Annotated[str, Field(**docs.calibre_title_sort)] = ""
    """The alphabeticaly correct sorting title, for example `The Story Of All of Us` 
    would be sorted as `Story Of All Of Us, The`."""

    series: Annotated[str, Field(**docs.calibre_series)] = ""
    """The book series title."""

    series_index: Annotated[int, Field(**docs.calibre_series_index)] = 1
    """The index within the book series."""

    author_link_map: Annotated[str, Field(**docs.calibre_author_link_map)] = ""
    """The author name link map, for example `Author Name <https://author-website.com>`."""
