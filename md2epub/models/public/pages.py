from __future__ import annotations

from pathlib import Path
from typing import Annotated, Any

from pydantic import Field, model_validator

from md2epub.core.environment import get_environment
from md2epub.models.public import docs
from md2epub.models.public.book_content import Book, BookContentName, OpfGuideType, Page, PageType
from md2epub.utils.utils import safe_join

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

    images: Annotated[list[Path], Field(default_factory=list, **docs.title_page_images)]
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

    sources: Annotated[dict[str, Path], Field(default_factory=dict, **docs.custom_sources)]
    """Named source files made available to the template, keyed by whatever name the template expects."""

    values: Annotated[dict[Any, Any], Field(default_factory=dict, **docs.custom_values)]
    """Arbitrary values passed straight through to the template, keyed by whatever name it expects."""

    def template_path(self, base_dir: Path) -> Path:
        return safe_join(base_dir, self.template)


class SubBook(Page, validate_assignment=True):
    """
    Represents a sub-book or part of the book. This page type is used to group chapters and other
    content into a logical section of the book. It can contain its own metadata, pages, and
    settings, allowing for the creation of complex book structures within a single EPUB file.
    """

    TYPE = PageType.Book
    DEFAULT_TEMPLATE = None

    include_file: Annotated[Path | None, Field(**docs.include_file)] = None
    """Optional book manifest file from which to include whole subbook definition.
    This path must be relative to main manifest."""

    book: Annotated[Book, Field(**docs.subbook_book)]
    """Subbook that belong to this part of the book."""

    @model_validator(mode="before")
    @classmethod
    def on_before_model_validate(cls, data: Any) -> Any:
        # If include_file is valid, try to load it as a parent Config.
        if include_file := data.get("include_file"):
            env = get_environment()

            include_file = safe_join(env.work_dir, include_file)
            if not include_file.exists() or not include_file.is_file():
                raise ValueError(f"Invalid include file: '{include_file}' does not exist or is not a file.")

            # Load the manifest book file. It always has a `name` by now (explicit, or derived from its
            # own folder by `Book.create()`), so mirror it here unless this page already has its own.
            data["book"] = Book.load_from_file(include_file)
            data.setdefault("name", data["book"].name)

        # If include_file is not set, `name` has no folder to come from - BookContent.name stays
        # required, same as for any other page.
        return data
