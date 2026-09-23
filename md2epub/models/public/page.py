from __future__ import annotations

from enum import StrEnum, auto
from pathlib import Path
from typing import Annotated, Any, ClassVar

from pydantic import BaseModel, Field, computed_field, field_validator

from md2epub.core.environment import get_environment
from md2epub.models.public.common import Author, Contributor, Identifier
from md2epub.models.public.docs import manifest as manifest_docs
from md2epub.models.public.docs import page as docs
from md2epub.utils.utils import safe_join

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
    Md2Epub = auto()
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


# region Content base model


# Not only dots (`.`, `..`), otherwise the name could point to a parent folder.
# No look-around: pydantic uses the Rust regex engine, which doesn't support it.
BOOK_CONTENT_NAME_PATTERN = r"^\.*[A-Za-z0-9_-][A-Za-z0-9._-]*$"

BookContentName = Annotated[str, Field(pattern=BOOK_CONTENT_NAME_PATTERN, **docs.book_content_name)]


class BookContent(BaseModel, validate_assignment=True):
    """Base model for book content, including pages and other elements."""

    name: Annotated[BookContentName, Field()]
    """Custon name of the book content."""

    toc_title: Annotated[str | None, Field(**docs.toc_title)] = None
    """Optional label to show in the table of contents instead of the default one (a chapter's own
    heading, a sub-book's title, or as a last resort its technical `name`)."""

    stylesheets: Annotated[set[Path], Field(**docs.stylesheets)] = set()
    """Set of stylesheets to be included in the EPUB for this content."""

    stylesheets_overrides: Annotated[set[Path], Field(**docs.stylesheets_overrides)] = set()
    """Set of stylesheets to override existing stylesheets in the EPUB for this content."""


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

    @computed_field
    @property
    def template_path(self) -> Path:
        """
        Return the path to the template for this page. If a custom template is set, return that;
        otherwise, return the default template for the page type.
        """
        env = get_environment()

        # If a custom template is set, return that. Otherwise, return the default template path
        # for the page type if it exists. If neither is set, return None.
        if self.custom_template is not None:
            return safe_join(env.work_dir, self.custom_template)
        elif self.DEFAULT_TEMPLATE is not None:
            return env.template_dir / self.DEFAULT_TEMPLATE
        else:
            raise RuntimeError("Template path is not valid!")


# region Page subclasses


class CoverPage(Page, validate_assignment=True):
    """Represents the cover page of the book."""

    TYPE = PageType.Cover
    DEFAULT_TEMPLATE = Path("cover.xhtml.jinja")

    name: Annotated[BookContentName, Field()] = "cover"
    opf_spine_add: Annotated[bool, Field(**docs.opf_spine_add)] = True
    opf_guide_type: Annotated[OpfGuideType | None, Field(**docs.opf_guide_type)] = OpfGuideType.Cover
    opf_guide_title: Annotated[str, Field(**docs.opf_guide_title)] = "Cover"

    cover_image: Annotated[Path, Field(**docs.cover_image)] = Path("images/cover.jpg")
    """Path to the cover image, relative to the manifest's folder."""


class TitlePage(Page, validate_assignment=True):
    """Represents the title page of the book."""

    TYPE = PageType.Title
    DEFAULT_TEMPLATE = Path("title.xhtml.jinja")

    name: Annotated[BookContentName, Field()] = "title"
    opf_spine_add: Annotated[bool, Field(**docs.opf_spine_add)] = True
    opf_guide_type: Annotated[OpfGuideType | None, Field(**docs.opf_guide_type)] = OpfGuideType.TitlePage
    opf_guide_title: Annotated[str, Field(**docs.opf_guide_title)] = "Title"

    images: Annotated[list[Path], Field(**docs.title_page_images)] = []
    """Images shown on the title page, in order, above the book's metadata."""

    render_title: Annotated[bool, Field(**docs.render_title)] = True
    """Whether the title page shows the book's title, subtitle and author."""

    render_metadata: Annotated[bool, Field(**docs.render_metadata)] = True
    """Whether the title page shows the book's publisher, description, rights and identifiers."""

    additional_content: Annotated[Path | None, Field(**docs.additional_content)] = None
    """Path to a Markdown file whose rendered content is appended to the title page, if given."""


class TocPage(Page, validate_assignment=True):
    """Represents the table of contents page of the book."""

    TYPE = PageType.Toc
    DEFAULT_TEMPLATE = Path("toc.xhtml.jinja")

    name: Annotated[BookContentName, Field()] = "toc"
    opf_spine_add: Annotated[bool, Field(**docs.opf_spine_add)] = True
    opf_guide_type: Annotated[OpfGuideType | None, Field(**docs.opf_guide_type)] = OpfGuideType.TOC
    opf_guide_title: Annotated[str, Field(**docs.opf_guide_title)] = "Table of Contents"

    title: Annotated[str, Field(**docs.toc_page_title)] = "Table of Contents"
    """The heading shown at the top of the table of contents page itself."""

    render_links: Annotated[bool, Field(**docs.render_links)] = True
    """Whether table of contents entries are rendered as links to their target page."""

    render_depth: Annotated[int, Field(**docs.render_depth)] = 2
    """How many nesting levels of the table of contents are rendered (sub-books count as one level)."""


class Chapter(Page, validate_assignment=True):
    """Represents a chapter page of the book."""

    TYPE = PageType.Chapter
    DEFAULT_TEMPLATE = Path("chapter.xhtml.jinja")

    name: Annotated[BookContentName, Field()] = "chapter"
    opf_spine_add: Annotated[bool, Field(**docs.opf_spine_add)] = True
    add_to_toc: Annotated[bool, Field(**docs.add_to_toc)] = True

    source: Annotated[Path, Field(**docs.chapter_source)]
    """Path to the chapter's Markdown source, relative to the manifest's folder."""

    sequence: Annotated[str | None, Field(**docs.chapter_sequence)] = "default"
    """Reserved for future use in ordering or grouping chapters."""


class CustomPage(Page, validate_assignment=True):
    """
    Custom page type for user-defined content. This page type allows for the inclusion of custom
    content in the EPUB, with the option to specify a custom template.
    """

    TYPE = PageType.Custom
    DEFAULT_TEMPLATE = None

    template: Annotated[Path, Field(**docs.custom_template_path)]
    """Path to the Jinja template that renders this page, relative to the manifest's folder."""

    sources: Annotated[dict[str, Path], Field(**docs.custom_sources)] = {}
    """Named source files made available to the template, keyed by whatever name the template expects."""

    values: Annotated[dict[Any, Any], Field(**docs.custom_values)] = {}
    """Arbitrary values passed straight through to the template, keyed by whatever name it expects."""

    @computed_field
    @property
    def template_path(self) -> Path:
        return safe_join(get_environment().work_dir, self.template)


class SubBook(Page, validate_assignment=True):
    """
    Represents a sub-book or part of the book. This page type is used to group chapters and other
    content into a logical section of the book. It can contain its own metadata, pages, and
    settings, allowing for the creation of complex book structures within a single EPUB file.
    """

    TYPE = PageType.Book
    DEFAULT_TEMPLATE = None

    name: Annotated[BookContentName, Field()] = "subbook"
    """Name of the page."""

    book: Annotated[Book, Field(**docs.subbook_book)]
    """Subbook that belong to this part of the book."""


# region Book


class Book(BookContent, validate_assignment=True):
    """Represents a book in the EPUB format."""

    # Book metadata

    supertitle: Annotated[str, Field(**manifest_docs.manifest_supertitle)] = ""
    """The supertitle of the content, used as a higher-level title."""

    title: Annotated[str, Field(**manifest_docs.manifest_title)] = ""
    """The title of the content, used as the main title."""

    subtitle: Annotated[str, Field(**manifest_docs.manifest_subtitle)] = ""
    """The subtitle of the content, used as a secondary title."""

    author: Annotated[Author | None, Field(**manifest_docs.manifest_author)] = None
    """The main author of the book."""

    language: Annotated[str, Field(**manifest_docs.manifest_language)] = ""
    """The language of the book."""

    created: Annotated[str | int | None, Field(**manifest_docs.manifest_created)] = None
    """The date the book was created."""

    identifiers: Annotated[list[Identifier], Field(**manifest_docs.manifest_identifiers)] = []
    """A list of identifiers for the book."""

    subjects: Annotated[list[str], Field(**manifest_docs.manifest_subjects)] = []
    """A list of subjects for the book."""

    description: Annotated[str, Field(**manifest_docs.manifest_description)] = ""
    """A description of the book."""

    publisher: Annotated[str, Field(**manifest_docs.manifest_publisher)] = ""
    """The publisher of the book."""

    contributors: Annotated[list[Contributor], Field(**manifest_docs.manifest_contributors)] = []
    """A list of contributors to the book."""

    rights: Annotated[list[str], Field(**manifest_docs.manifest_rights)] = []
    """A list of rights statements for the book."""

    # Additional book settings

    title_separator: Annotated[str, Field(**docs.book_title_separator)] = " - "
    """The separator to use between the title and subtitle of the book."""

    files: Annotated[set[Path], Field(**docs.book_files)] = set()
    """All files and folders needed by this book to be included in the EPUB. This includes all files
    and folders needed by the pages, as well as any additional files and folders specified
    in the manifest."""

    pages: Annotated[list[Page], Field(**docs.book_pages)]
    """List of pages in order to render in ePub."""

    @field_validator("supertitle", "title", "subtitle", mode="before")
    @classmethod
    def validate_titles(cls, val):
        # If value set to none from yaml (empty), than change it to empty string
        if val is None:
            return ""

        return val

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
                case PageType.Md2Epub:
                    # TODO: create app copyright page
                    pass
                case _:
                    raise RuntimeError(f"Cannot create page! Invalid page type '{type}'.")

        return pages
