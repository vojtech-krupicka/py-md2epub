"""Manifest model: loading from YAML/JSON, defaults and the page shorthand syntax."""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from textwrap import dedent

import pytest
from pydantic import ValidationError

from md2epub.models.public.book_content import Book
from md2epub.models.public.pages import Chapter, CoverPage, CustomPage, SubBook, TitlePage, TocPage


def load(text: str) -> Book:
    return Book.load_from_string(dedent(text))


MINIMAL = dedent(
    """
    name: content
    pages: [text/ch1.md]
    metadata:
        title: Test Book
    """
)

# region Defaults and metadata


class TestMetadata:
    def test_minimal_manifest_gets_defaults(self):
        m = load(MINIMAL)

        assert m.metadata.title == "Test Book"
        assert m.metadata.language == "en"
        assert re.fullmatch(r"\d{4}", str(m.metadata.created))
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(m.metadata.published))
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(m.metadata.modified))
        assert m.metadata.book_id.scheme == "uuid"
        assert uuid.UUID(m.metadata.book_id.value)

    def test_book_id_is_stable_for_the_same_title_and_author(self):
        """Rebuilding the same, unchanged book must not hand it a new identity every time (readers key on it)."""
        manifest = MINIMAL + "    author: Jane Doe\n"

        assert load(manifest).metadata.book_id.value == load(manifest).metadata.book_id.value

    def test_book_id_changes_with_the_title(self):
        """Control: this holds both before and after the fix (random or derived, different input differs)."""
        a = load(MINIMAL + "    author: Jane Doe\n")
        b = load(MINIMAL.replace("Test Book", "A Different Book") + "author: Jane Doe\n")

        assert a.metadata.book_id.value != b.metadata.book_id.value

    def test_book_id_changes_with_the_author(self):
        """Control: this holds both before and after the fix (random or derived, different input differs)."""
        a = load(MINIMAL + "    author: Jane Doe\n")
        b = load(MINIMAL + "    author: John Smith\n")

        assert a.metadata.book_id.value != b.metadata.book_id.value

    def test_explicit_book_id_is_kept(self):
        """An id the user picked on purpose (e.g. a real ISBN-derived UUID) must never be overridden."""
        m = load(MINIMAL + "    book_id: {value: my-custom-id}\n")

        assert m.metadata.book_id.value == "my-custom-id"

    @pytest.mark.parametrize("blank", ["", "   "])
    def test_blank_explicit_book_id_value_is_treated_as_unset(self, blank: str):
        """`book_id: {value: ''}` (or all-whitespace) must not ship an empty <dc:identifier> - derive one instead."""
        m = load(MINIMAL + f"book_id: {{value: {blank!r}}}\n")

        assert m.metadata.book_id.value
        assert m.metadata.book_id.value.strip() == m.metadata.book_id.value

    def test_full_title(self):
        assert load(MINIMAL).full_title == "Test Book"
        assert load(MINIMAL + "\n    subtitle: The Sequel").full_title == "Test Book - The Sequel"

    def test_author_shorthand(self):
        m = load(MINIMAL + "    author: Jane Doe\n")

        assert m.metadata.author.name == "Jane Doe"
        assert m.metadata.author.role == "aut"
        assert m.metadata.author.file_as == "Doe, Jane"

    def test_author_full_form_keeps_file_as(self):
        m = load(
            """
            metadata:
                title: T
                author: {name: Jane Doe, file_as: "Doe, J."}
            name: content
            pages: [text/ch1.md]
            """
        )

        assert m.metadata.author.file_as == "Doe, J."

    def test_metadata_is_copied_to_root_book(self):
        m = load(
            """
            metadata:
                title: Test Book
                subtitle: Sub
                author: Jane Doe
                language: cs
                publisher: ACME
            name: content
            pages: [text/ch1.md]
            """
        )

        assert m.metadata.title == "Test Book"
        assert m.metadata.subtitle == "Sub"
        assert m.metadata.author and m.metadata.author.name == "Jane Doe"
        assert m.metadata.language == "cs"
        assert m.metadata.publisher == "ACME"

    def test_title_is_required(self):
        with pytest.raises(ValidationError, match="metadata.title"):
            load("name: content\npages: [text/ch1.md]\nmetadata: {}")


# region Pages


class TestPages:
    def test_plain_string_is_a_chapter(self):
        (page,) = load(MINIMAL).pages

        assert isinstance(page, Chapter)
        assert page.source == Path("text/ch1.md")

    def test_missing_type_defaults_to_chapter(self):
        m = load(
            """
            metadata:
                title: T
            name: content
            pages: [{source: text/ch1.md, name: first}]
            """
        )

        assert isinstance(m.pages[0], Chapter)
        assert m.pages[0].name == "first"

    def test_typed_pages_keep_their_order(self):
        m = load(
            """
            metadata:
                title: T
            name: content
            pages:
            - type: cover
            - type: title
            - type: toc
            - text/ch1.md
            """
        )

        assert [type(p) for p in m.pages] == [CoverPage, TitlePage, TocPage, Chapter]

    @pytest.mark.parametrize(
        ("shorthand", "expected"),
        [
            ("cover_title_toc", [CoverPage, TitlePage, TocPage]),
            ("cover_title", [CoverPage, TitlePage]),
            ("cover_toc", [CoverPage, TocPage]),
            ("title_toc", [TitlePage, TocPage]),
        ],
    )
    def test_multi_page_shorthands(self, shorthand: str, expected: list[type]):
        m = load(f"""
            name: content
            pages: [{{type: {shorthand}}}]
            metadata: 
                title: T
        """)

        assert [type(p) for p in m.pages] == expected

    def test_unknown_page_type_is_rejected(self):
        # Currently a bare RuntimeError escapes from the validator, a ValidationError would be nicer.
        with pytest.raises((ValidationError, RuntimeError)):
            load("metadata: {title: T}\nname: content\npages: [{type: nonsense}]")

    def test_empty_pages_are_rejected(self):
        with pytest.raises(ValidationError):
            load("metadata: {title: T}\nname: content\npages: []")

    def test_chapter_requires_a_source(self):
        with pytest.raises(ValidationError):
            load("metadata: {title: T}\nname: content\npages: [{type: chapter}]")

    def test_custom_page_requires_a_template(self):
        # `name` is given on purpose, so that only the missing template can be the reason for the error.
        with pytest.raises(ValidationError, match="template"):
            load("""
                metadata: 
                    title: T
                name: content
                pages: [{type: custom, name: cp}]
            """)

    def test_custom_page_requires_a_name(self):
        # custom page requires a `name`
        with pytest.raises(ValidationError, match="pages.name"):
            load("""
                metadata:
                    title: T
                name: content
                pages: [{type: custom, template: my.jinja}]
            """)

    def test_custom_page(self):
        m = load(
            """
            metadata:
                title: T
            name: content
            pages:
              - {type: custom, name: cp, template: my.jinja, values: {greeting: hi}}
            """
        )
        (page,) = m.pages

        assert isinstance(page, CustomPage)
        assert page.values == {"greeting": "hi"}

    def test_sub_book(self):
        m = load(
            """
            metadata:
                title: T
            name: content
            pages:
              - type: book
                name: part1
                book:
                  metadata:
                    title: Part One
                  name: part1
                  pages: [text/ch1.md]
            """
        )
        (page,) = m.pages

        assert isinstance(page, SubBook)
        assert page.book.name == "part1"
        assert isinstance(page.book.pages[0], Chapter)

    def test_book_requires_a_name(self):
        with pytest.raises(ValidationError, match="Book\nname"):
            load("""
                metadata:
                    title: T
                pages: [text/ch1.md]
            """)


# region Loading from files


class TestLoadFromFile:
    def test_yaml_file(self, tmp_path: Path):
        path = tmp_path / "manifest.yaml"
        path.write_text(dedent(MINIMAL), encoding="utf-8")

        m = Book.load_from_file(path)

        assert m.manifest_file == path
        assert m.metadata.title == "Test Book"

    def test_json_file(self, tmp_path: Path):
        path = tmp_path / "manifest.json"
        path.write_text('{"metadata": {"title": "JSON Book"}, "name": "content", "pages": ["text/ch1.md"]}')

        assert Book.load_from_file(path).metadata.title == "JSON Book"

    def test_utf8_content(self, tmp_path: Path):
        path = tmp_path / "manifest.yaml"
        path.write_text(
            """
            metadata:
                title: Zaklínač
            name: content
            pages: [text/ch1.md]
        """,
            encoding="utf-8",
        )

        assert Book.load_from_file(path).metadata.title == "Zaklínač"

    def test_other_suffix_is_rejected(self, tmp_path: Path):
        path = tmp_path / "manifest.txt"
        path.write_text(dedent(MINIMAL))

        with pytest.raises(RuntimeError, match="invalid manifest format"):
            Book.load_from_file(path)

    def test_uppercase_suffix(self, tmp_path: Path):
        path = tmp_path / "BOOK.YAML"
        path.write_text(dedent(MINIMAL), encoding="utf-8")

        assert Book.load_from_file(path).metadata.title == "Test Book"

    def test_load_from_string_json(self):
        m = Book.load_from_string('{"metadata": {"title": "T"}, "name": "c", "pages": ["a.md"]}', type="json")

        assert m.metadata.title == "T"

    def test_load_from_string_unknown_format(self):
        with pytest.raises(RuntimeError, match="invalid manifest format"):
            Book.load_from_string("x", type="toml")
