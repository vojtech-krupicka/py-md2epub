"""`ContentCreator`: Markdown source in, XHTML out."""

from __future__ import annotations

from pathlib import Path

import pytest

from md2epub.core.content_creator import ContentCreator
from md2epub.core.environment import Environment
from md2epub.models.public.manifest import Manifest
from tests.conftest import Project


@pytest.fixture
def creator(project: Project, env: Environment) -> ContentCreator:
    env.set_work_dir(project.root)
    return ContentCreator(Manifest.load_from_file(project.manifest_path))


class TestMarkdown:
    def test_basic_markdown(self, creator: ContentCreator):
        html = creator.from_markdown("# Title\n\nHello *world* & friends.\n")

        assert "<h1>Title</h1>" in html
        assert "<em>world</em>" in html
        assert "&amp;" in html

    def test_smart_quotes_use_the_configured_substitutions(self, creator: ContentCreator):
        assert "&bdquo;quotes&ldquo;" in creator.from_markdown('"quotes"')

    def test_vlna_keeps_single_letter_words_with_the_next_word(self, creator: ContentCreator):
        assert "k&nbsp;lesu" in creator.from_markdown("Šel k lesu")

    def test_fenced_code_and_tables_are_enabled(self, creator: ContentCreator):
        html = creator.from_markdown("```\ncode\n```\n\n| a | b |\n|---|---|\n| 1 | 2 |\n")

        assert "<code>code" in html
        assert "<table>" in html


class TestCreateFromPath:
    def test_reads_relative_to_the_work_dir(self, creator: ContentCreator):
        html = creator.create_from_path(Path("text/ch1.md"))

        assert "<h1>Chapter One</h1>" in html
        assert "<em>world</em>" in html

    def test_missing_file(self, creator: ContentCreator):
        with pytest.raises(FileNotFoundError):
            creator.create_from_path(Path("text/nope.md"))

    def test_unsupported_content_type(self, creator: ContentCreator, project: Project):
        project.write("text/notes.txt", "plain")

        with pytest.raises(RuntimeError):
            creator.create_from_path(Path("text/notes.txt"))

    def test_byte_order_mark_is_stripped(self, creator: ContentCreator, project: Project):
        project.write("text/bom.md", chr(0xFEFF) + "# Title\n")  # a UTF-8 byte order mark

        assert "<h1>Title</h1>" in creator.create_from_path(Path("text/bom.md"))

    @pytest.mark.xfail(
        strict=True,
        reason='`str(lxml.tostring(...))` returns the repr of a bytes object ("b\'<div>...") instead of decoded text',
    )
    def test_result_is_xhtml_text_not_a_bytes_repr(self, creator: ContentCreator):
        html = creator.create_from_path(Path("text/ch1.md"))

        assert not html.startswith("b'")
        assert "\\xe2" not in html
