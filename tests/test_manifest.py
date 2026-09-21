"""Manifest model: loading from YAML/JSON, defaults and the page shorthand syntax."""

from __future__ import annotations

import re
import uuid
from pathlib import Path
from textwrap import dedent

import pytest
from pydantic import ValidationError

from md2epub.models.public.manifest import Manifest
from md2epub.models.public.page import Chapter, CoverPage, CustomPage, SubBook, TitlePage, TocPage


def load(text: str) -> Manifest:
    return Manifest.load_from_string(dedent(text))


MINIMAL = dedent(
    """
    title: Test Book
    book:
      name: content
      pages: [text/ch1.md]
    """
)

# region Defaults and metadata


class TestMetadata:
    def test_minimal_manifest_gets_defaults(self):
        m = load(MINIMAL)

        assert m.title == "Test Book"
        assert m.language == "en"
        assert re.fullmatch(r"\d{4}", str(m.created))
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(m.published))
        assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(m.modified))
        assert m.book_id.scheme == "uuid"
        assert uuid.UUID(m.book_id.value)

    @pytest.mark.xfail(
        strict=True,
        reason="`book_id: BookId = BookId()` is evaluated once at import: every manifest in a process shares one UUID",
    )
    def test_every_manifest_gets_its_own_book_id(self):
        assert load(MINIMAL).book_id.value != load(MINIMAL).book_id.value

    def test_full_title(self):
        assert load(MINIMAL).full_title == "Test Book"
        assert load(MINIMAL + "\nsubtitle: The Sequel").full_title == "Test Book - The Sequel"

    def test_author_shorthand(self):
        m = load(MINIMAL + "author: Jane Doe\n")

        assert m.author.name == "Jane Doe"
        assert m.author.role == "aut"
        assert m.author.file_as == "Doe, Jane"

    def test_author_full_form_keeps_file_as(self):
        m = load(
            """
            title: T
            author: {name: Jane Doe, file_as: "Doe, J."}
            book: {name: content, pages: [text/ch1.md]}
            """
        )

        assert m.author.file_as == "Doe, J."

    def test_metadata_is_copied_to_root_book(self):
        m = load(
            """
            title: Test Book
            subtitle: Sub
            author: Jane Doe
            language: cs
            publisher: ACME
            book: {name: content, pages: [text/ch1.md]}
            """
        )

        assert m.book.title == "Test Book"
        assert m.book.subtitle == "Sub"
        assert m.book.author.name == "Jane Doe"
        assert m.book.language == "cs"
        assert m.book.publisher == "ACME"

    def test_title_is_required(self):
        with pytest.raises(ValidationError):
            load("book: {name: content, pages: [text/ch1.md]}")


# region Pages


class TestPages:
    def test_plain_string_is_a_chapter(self):
        (page,) = load(MINIMAL).book.pages

        assert isinstance(page, Chapter)
        assert page.source == Path("text/ch1.md")

    def test_missing_type_defaults_to_chapter(self):
        m = load(
            """
            title: T
            book: {name: content, pages: [{source: text/ch1.md, name: first}]}
            """
        )

        assert isinstance(m.book.pages[0], Chapter)
        assert m.book.pages[0].name == "first"

    def test_typed_pages_keep_their_order(self):
        m = load(
            """
            title: T
            book:
              name: content
              pages:
                - type: cover
                - type: title
                - type: toc
                - text/ch1.md
            """
        )

        assert [type(p) for p in m.book.pages] == [CoverPage, TitlePage, TocPage, Chapter]

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
        m = load(f"title: T\nbook: {{name: content, pages: [{{type: {shorthand}}}]}}")

        assert [type(p) for p in m.book.pages] == expected

    def test_unknown_page_type_is_rejected(self):
        # Currently a bare RuntimeError escapes from the validator, a ValidationError would be nicer.
        with pytest.raises((ValidationError, RuntimeError)):
            load("title: T\nbook: {name: content, pages: [{type: nonsense}]}")

    def test_empty_pages_are_rejected(self):
        with pytest.raises(ValidationError):
            load("title: T\nbook: {name: content, pages: []}")

    def test_chapter_requires_a_source(self):
        with pytest.raises(ValidationError):
            load("title: T\nbook: {name: content, pages: [{type: chapter}]}")

    def test_custom_page_requires_a_template(self):
        # `name` is given on purpose, so that only the missing template can be the reason for the error.
        with pytest.raises(ValidationError, match="template"):
            load("title: T\nbook: {name: content, pages: [{type: custom, name: cp}]}")

    @pytest.mark.xfail(
        strict=True,
        reason="CustomPage has no default `name` (every other page type has one, the old model had 'custom')",
    )
    def test_custom_page_name_has_a_default(self):
        load("title: T\nbook: {name: content, pages: [{type: custom, template: my.jinja}]}")

    def test_custom_page(self):
        m = load(
            """
            title: T
            book:
              name: content
              pages:
                - {type: custom, name: cp, template: my.jinja, values: {greeting: hi}}
            """
        )
        (page,) = m.book.pages

        assert isinstance(page, CustomPage)
        assert page.values == {"greeting": "hi"}

    def test_sub_book(self):
        m = load(
            """
            title: T
            book:
              name: content
              pages:
                - type: book
                  book:
                    name: part1
                    title: Part One
                    pages: [text/ch1.md]
            """
        )
        (page,) = m.book.pages

        assert isinstance(page, SubBook)
        assert page.book.name == "part1"
        assert isinstance(page.book.pages[0], Chapter)

    @pytest.mark.xfail(
        strict=True,
        reason="`book.name` has no default, so the README example (no `name`) fails - decide: default or fix README",
    )
    def test_book_name_is_optional(self):
        load("title: T\nbook: {pages: [text/ch1.md]}")


# region Loading from files


class TestLoadFromFile:
    def test_yaml_file(self, tmp_path: Path):
        path = tmp_path / "manifest.yaml"
        path.write_text(dedent(MINIMAL), encoding="utf-8")

        m = Manifest.load_from_file(path)

        assert m.title == "Test Book"
        assert m.file == path

    def test_json_file(self, tmp_path: Path):
        path = tmp_path / "manifest.json"
        path.write_text('{"title": "JSON Book", "book": {"name": "content", "pages": ["text/ch1.md"]}}')

        assert Manifest.load_from_file(path).title == "JSON Book"

    def test_utf8_content(self, tmp_path: Path):
        path = tmp_path / "manifest.yaml"
        path.write_text("title: Zaklínač\nbook: {name: content, pages: [text/ch1.md]}", encoding="utf-8")

        assert Manifest.load_from_file(path).title == "Zaklínač"

    def test_other_suffix_is_rejected(self, tmp_path: Path):
        path = tmp_path / "manifest.txt"
        path.write_text(dedent(MINIMAL))

        with pytest.raises(RuntimeError, match="invalid manifest format"):
            Manifest.load_from_file(path)

    @pytest.mark.xfail(
        strict=True,
        reason="`resolve_input` accepts `BOOK.YAML` (case-insensitive), `load_from_file` compares case-sensitively",
    )
    def test_uppercase_suffix(self, tmp_path: Path):
        path = tmp_path / "BOOK.YAML"
        path.write_text(dedent(MINIMAL), encoding="utf-8")

        assert Manifest.load_from_file(path).title == "Test Book"

    def test_load_from_string_json(self):
        m = Manifest.load_from_string('{"title": "T", "book": {"name": "c", "pages": ["a.md"]}}', type="json")

        assert m.title == "T"

    def test_load_from_string_unknown_format(self):
        with pytest.raises(RuntimeError, match="invalid manifest format"):
            Manifest.load_from_string("x", type="toml")
