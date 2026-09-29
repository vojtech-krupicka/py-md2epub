"""`init`: scaffold a starter manifest plus its folder structure."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest
import yaml

from md2epub.commands import build, init
from md2epub.models.public.book_content import Book
from tests.test_cli import invoke


class TestInitCommand:
    def test_creates_a_loadable_manifest(self, tmp_path: Path):
        out = tmp_path / "my-book"
        init.run(out)

        manifest = Book.load_from_file(out / "manifest.yaml")

        assert manifest.name == "my-book"
        assert manifest.metadata.title == "my-book"

    def test_creates_the_chapter_source_file(self, tmp_path: Path):
        out = tmp_path / "my-book"
        init.run(out)

        manifest = Book.load_from_file(out / "manifest.yaml")
        (chapter,) = [p for p in manifest.pages if hasattr(p, "source")]

        assert (out / chapter.source).is_file()

    def test_initialized_project_actually_builds(self, tmp_path: Path):
        """The whole point of `init`: `md2epub build` must work right away on what it creates."""
        out = tmp_path / "my-book"
        init.run(out)

        epub_path = tmp_path / "my-book.epub"
        build.run(out / "manifest.yaml", epub_path)

        assert epub_path.is_file()

    def test_initialized_project_chapter_text_is_present(self, tmp_path: Path):
        out = tmp_path / "my-book"
        init.run(out)
        epub_path = tmp_path / "my-book.epub"
        build.run(out / "manifest.yaml", epub_path)

        epub = zipfile.ZipFile(epub_path)
        assert "Chapter 01" in epub.read("OEBPS/chapters/chapter.xhtml").decode("utf-8")

    def test_output_directory_is_created(self, tmp_path: Path):
        out = tmp_path / "does" / "not" / "exist" / "yet"

        init.run(out)

        assert out.is_dir()
        assert (out / "manifest.yaml").is_file()

    def test_non_empty_output_directory_is_rejected(self, tmp_path: Path):
        out = tmp_path / "my-book"
        out.mkdir()
        (out / "existing.txt").write_text("already here")

        with pytest.raises(RuntimeError, match="not empty"):
            init.run(out)

    def test_name_and_title_use_the_resolved_output_path(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        """
        Regression: `run()` must not derive `name`/`title` from the raw, possibly-relative `output_dir`
        it was called with - `Path(".").name` is `""`, which fails `Book`'s `name` pattern outright.
        """
        out = tmp_path / "my-book"
        out.mkdir()
        monkeypatch.chdir(out)

        init.run(Path("."))

        manifest = Book.load_from_file(out / "manifest.yaml")
        assert manifest.name == "my-book"
        assert manifest.metadata.title == "my-book"

    def test_manifest_does_not_contain_computed_fields(self, tmp_path: Path):
        """`full_title`/`version` are derived read-only values, not something a manifest should carry."""
        out = tmp_path / "my-book"
        init.run(out)

        raw = yaml.safe_load((out / "manifest.yaml").read_text(encoding="utf-8"))

        assert "full_title" not in raw
        assert "version" not in raw


class TestInitCli:
    def test_help(self):
        result = invoke("init", "--help")

        assert result.exit_code == 0
        assert "output-dir" in result.output

    def test_cli_creates_a_buildable_project(self, tmp_path: Path, log_cfg: Path):
        out = tmp_path / "my-book"

        result = invoke("init", "--log-cfg-path", log_cfg, "-o", out)

        assert result.exit_code == 0, result.output
        assert (out / "manifest.yaml").is_file()
