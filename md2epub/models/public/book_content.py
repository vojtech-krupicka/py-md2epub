from __future__ import annotations

import abc
from enum import StrEnum, auto
from pathlib import Path
from typing import Annotated, Any, ClassVar

from pydantic import BaseModel, Field, SerializeAsAny, computed_field, field_validator

from md2epub import __version__
from md2epub.core.environment import get_environment
from md2epub.models.public import docs
from md2epub.models.public.config import Config
from md2epub.models.public.metadata import Metadata
from md2epub.utils.utils import safe_join, slugify

# region Enums


class PageType(StrEnum):
    """Type of page in the book."""

    Cover = auto()
    Title = auto()
    Toc = auto()
    Chapter = auto()
    Book = auto()
    Custom = auto()
    CoverTitleToc = "cover_title_toc"
    CoverTitle = "cover_title"
    CoverToc = "cover_toc"
    TitleToc = "title_toc"
    DefaultBeginPages = "default_begin_pages"
    DefaultAfterPages = "default_after_pages"
    Copyright = auto()
    _Unknown = "unknown"

    @classmethod
    def _missing_(cls, value):
        return PageType._Unknown


class OpfGuideType(StrEnum):
    """Type of guide entry in the OPF file."""

    Cover = auto()
    TitlePage = "title-page"
    TOC = auto()
    Index = auto()
    LOI = auto()
    LOT = auto()
    Notes = auto()
    Preface = auto()
    Text = auto()


# region Book Content

# Not only dots (`.`, `..`), otherwise the name could point to a parent folder.
# No look-around: pydantic uses the Rust regex engine, which doesn't support it.

BOOK_CONTENT_NAME_PATTERN = r"^\.*[A-Za-z0-9_-][A-Za-z0-9._-]*$"

BookContentName = Annotated[str, Field(pattern=BOOK_CONTENT_NAME_PATTERN, **docs.book_content_name)]


class BookContent(abc.ABC, BaseModel, validate_assignment=True):
    """Base model for book content, including pages and other elements."""

    name: Annotated[BookContentName, Field()]
    """Custon name of the book content."""

    toc_title: Annotated[str | None, Field(**docs.book_content_toc_title)] = None
    """Optional label to show in the table of contents instead of the default one (a chapter's own
    heading, a sub-book's title, or as a last resort its technical `name`)."""

    stylesheets: Annotated[set[Path], Field(**docs.book_content_stylesheets)] = set()
    """Set of stylesheets to be included in the EPUB for this content."""

    stylesheets_overrides: Annotated[set[Path], Field(**docs.book_content_stylesheets_overrides)] = set()
    """Set of stylesheets to override existing stylesheets in the EPUB for this content."""

    files: Annotated[set[Path], Field(**docs.book_content_files)] = set()
    """All files and folders needed by this book to be included in the EPUB. This includes all files
    and folders needed by the pages, as well as any additional files and folders specified
    in the manifest."""


# region Page model


class Page(BookContent, validate_assignment=True):
    """Base model for a page in the book, including type, template, and other attributes."""

    TYPE: ClassVar[PageType]
    """The type of the page, used to determine how it is rendered in the EPUB."""

    DEFAULT_TEMPLATE: ClassVar[Path | None]
    """The default template for the page, used if no custom template is specified."""

    opf_spine_add: Annotated[bool, Field(**docs.opf_spine_add)] = False
    """Whether to add this page to the spine of the EPUB."""

    opf_spine_aux: Annotated[bool, Field(**docs.opf_spine_aux)] = False
    """Whether to add this page to the auxiliary spine of the EPUB."""

    opf_guide_type: Annotated[OpfGuideType | None, Field(**docs.opf_guide_type)] = None
    """The type of guide entry for this page in the OPF file."""

    opf_guide_title: Annotated[str, Field(**docs.opf_guide_title)] = ""
    """The title of the guide entry for this page in the OPF file."""

    add_to_toc: Annotated[bool, Field(**docs.add_to_toc)] = False
    """Whether to add this page to the table of contents of the EPUB."""

    custom_template: Annotated[Path | None, Field(**docs.custom_template)] = None
    """Optional custom template for rendering this page. If not set, the default template for the
    page type will be used."""

    @computed_field
    @property
    def type(self) -> PageType:
        """Return the type of the page."""
        return self.TYPE

    def template_path(self, base_dir: Path) -> Path:
        """
        Return the path to the template for this page. If a custom template is set, return that
        (resolved relative to `base_dir` - the folder of whichever manifest actually set it, not
        necessarily the root manifest's); otherwise, return the default template for the page type.
        """
        env = get_environment()

        # If a custom template is set, return that. Otherwise, return the default template path
        # for the page type if it exists. If neither is set, return None.
        if self.custom_template is not None:
            return safe_join(base_dir, self.custom_template)
        elif self.DEFAULT_TEMPLATE is not None:
            return env.template_dir / self.DEFAULT_TEMPLATE
        else:
            raise RuntimeError("Template path is not valid!")


# region Book model


class Book(BookContent, validate_assignment=True):
    """Represents a book in the EPUB format."""

    manifest_file: Annotated[Path | None, Field(**docs.manifest_file)] = None
    """The path to the book manifest file."""

    metadata: Annotated[Metadata, Field()]
    """EPUB/OPF metadata."""

    config: Annotated[Config, Field(default_factory=Config, **docs.book_config)]
    """Config model for markdown converter."""

    pages: Annotated[list[SerializeAsAny[Page]], Field(**docs.book_pages)]
    """List of pages in order to render in ePub."""

    @computed_field
    @property
    def full_title(self) -> str:
        """Return the full title of the book, including subtitle if present."""
        return f"{self.metadata.title} - {self.metadata.subtitle}" if self.metadata.subtitle else self.metadata.title

    @computed_field
    @property
    def version(self) -> str:
        """Return the version of the md2epub package."""
        return __version__

    @field_validator("pages", mode="before")
    @classmethod
    def validate_pages(cls: type, val: list[dict]) -> list[Page] | None:
        if not isinstance(val, list) or not len(val):
            return None

        pages: list[Page] = []

        for data in val:
            # Allow string values in pages definition as chapter source
            if isinstance(data, str):
                data = {"type": "chapter", "source": data}

            from md2epub.models.public.pages import Chapter, CoverPage, CustomPage, SubBook, TitlePage, TocPage

            # If type is missing, assume it is a chapter
            type = PageType(data.pop("type", "chapter"))

            # Create models for each page
            match type:
                case PageType.Cover:
                    pages.append(CoverPage(**data))
                case PageType.Title:
                    pages.append(TitlePage(**data))
                case PageType.Toc:
                    pages.append(TocPage(**data))
                case PageType.Chapter:
                    pages.append(Chapter(**data))
                case PageType.Custom:
                    pages.append(CustomPage(**data))
                case PageType.Book:
                    pages.append(SubBook(**data))
                case PageType.CoverTitleToc:
                    pages.append(CoverPage(**data))
                    pages.append(TitlePage(**data))
                    pages.append(TocPage(**data))
                case PageType.CoverTitle:
                    pages.append(CoverPage(**data))
                    pages.append(TitlePage(**data))
                case PageType.CoverToc:
                    pages.append(CoverPage(**data))
                    pages.append(TocPage(**data))
                case PageType.TitleToc:
                    pages.append(TitlePage(**data))
                    pages.append(TocPage(**data))
                case PageType.DefaultBeginPages:
                    # No pre default pages yet, return immediatly
                    pass
                case PageType.DefaultAfterPages:
                    # No post default pages yet, return immediatly
                    pass
                case PageType.Copyright:
                    # TODO: create app copyright page
                    pass
                case _:
                    raise RuntimeError(f"Cannot create page! Invalid page type '{type}'.")

        return pages

    @classmethod
    def load_from_file(cls, input: Path, encoding: str = "utf-8") -> Book:
        """Load book manifest from file. The file can be in JSON or YAML format."""

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

        return Book.create(input, data)

    @classmethod
    def load_from_string(cls, text: str, type: str = "yaml") -> Book:
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

        return Book.create(Path(), data)

    @classmethod
    def create(cls, input: Path, data: dict[str, Any]) -> Book:
        """
        Create manifest from data dictionary. Use input as the file field.

        If `name` is not set, derive it from the manifest's own folder (slugified), so a project's root
        manifest - and a sub-book loaded via `include_file` - do not have to repeat a name that is
        already implied by where the file lives. Falls back to requiring an explicit `name` (the usual
        "Field required" error) when there is no real folder to derive one from, or nothing usable in it.
        """
        if "name" not in data and input != Path():
            slug = slugify(input.parent.name)
            if slug:
                data["name"] = slug

        return Book(manifest_file=input, **data)
