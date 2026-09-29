"""
`include_file`: loading a whole sub-book (`SubBook.include_file`) or a shared config snippet
(`Config.include_file`) from another file.
"""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest
import yaml
from pydantic import ValidationError

from md2epub.commands import build
from md2epub.core.environment import Environment
from md2epub.models.public.book_content import Book
from tests.conftest import Project
from tests.helpers import NS, build_or_refuse, leaks, xml


def write_part(project: Project, folder: str, **data) -> Path:
    """Write a standalone sub-book manifest under `<project.root>/<folder>/manifest.yaml`."""
    payload = {"metadata": {"title": "Part One"}, "pages": [{"type": "toc"}, "text/ch1.md"]}
    payload.update(data)
    return project.write(f"{folder}/manifest.yaml", yaml.safe_dump(payload))


# region SubBook.include_file: paths resolve against the included book's own folder


class TestSubBookIncludeFile:
    def test_included_books_own_chapter_is_read_from_its_own_folder(self, project: Project):
        """The whole point of `include_file`: a standalone manifest builds unchanged, included or not."""
        project.write("part1/text/ch1.md", "# Part One Chapter\n\nPart one body.\n")
        write_part(project, "part1")
        project.manifest(
            book={"pages": [{"type": "toc"}, {"type": "book", "include_file": "part1/manifest.yaml"}]}
        )

        epub = zipfile.ZipFile(project.build())

        assert "OEBPS/part1/text/ch1.xhtml" in epub.namelist()
        assert "Part one body" in epub.read("OEBPS/part1/text/ch1.xhtml").decode("utf-8")

    def test_two_included_books_do_not_collide(self, project: Project):
        """Two included books using the same relative chapter name must not overwrite each other."""
        project.write("part1/text/ch1.md", "# One\n\nFirst part.\n")
        project.write("part2/text/ch1.md", "# Two\n\nSecond part.\n")
        write_part(project, "part1")
        write_part(project, "part2")
        project.manifest(
            book={
                "pages": [
                    {"type": "toc"},
                    {"type": "book", "include_file": "part1/manifest.yaml"},
                    {"type": "book", "include_file": "part2/manifest.yaml"},
                ]
            }
        )

        epub = zipfile.ZipFile(project.build())

        assert "First part" in epub.read("OEBPS/part1/text/ch1.xhtml").decode("utf-8")
        assert "Second part" in epub.read("OEBPS/part2/text/ch1.xhtml").decode("utf-8")

    def test_included_manifest_still_builds_standalone(self, project: Project, tmp_path: Path):
        """The same file used by the test above must also be a valid, buildable manifest on its own."""
        project.write("part1/text/ch1.md", "# Part One Chapter\n\nPart one body.\n")
        part1 = write_part(project, "part1")

        out = tmp_path / "standalone.epub"
        build.run(part1, out, True)

        assert zipfile.ZipFile(out).read("OEBPS/text/ch1.xhtml").decode("utf-8").find("Part one body") != -1

    def test_name_is_derived_from_the_included_folder(self, project: Project, env: Environment):
        env.set_work_dir(project.root)
        write_part(project, "part1")  # no explicit `name` in part1/manifest.yaml
        project.manifest(
            book={"pages": [{"type": "toc"}, {"type": "book", "include_file": "part1/manifest.yaml"}]}
        )

        (sub_book,) = Book.load_from_file(project.manifest_path).pages[1:]

        assert sub_book.name == "part1"
        assert sub_book.book.name == "part1"

    def test_explicit_name_in_the_included_manifest_is_kept(self, project: Project, env: Environment):
        env.set_work_dir(project.root)
        write_part(project, "part1", name="custom-name")
        project.manifest(
            book={"pages": [{"type": "toc"}, {"type": "book", "include_file": "part1/manifest.yaml"}]}
        )

        (sub_book,) = Book.load_from_file(project.manifest_path).pages[1:]

        assert sub_book.book.name == "custom-name"

    def test_include_file_cannot_escape_the_project(self, project: Project, env: Environment, outside: Path):
        env.set_work_dir(project.root)
        project.manifest(
            book={"pages": [{"type": "toc"}, {"type": "book", "include_file": "../outside/manifest.yaml"}]}
        )

        with pytest.raises(ValidationError):
            Book.load_from_file(project.manifest_path)

    def test_missing_include_file_is_rejected(self, project: Project, env: Environment):
        env.set_work_dir(project.root)
        project.manifest(
            book={"pages": [{"type": "toc"}, {"type": "book", "include_file": "does-not-exist.yaml"}]}
        )

        with pytest.raises(ValidationError):
            Book.load_from_file(project.manifest_path)


# region Root book name


class TestRootBookName:
    def test_name_is_derived_from_the_manifest_folder_when_not_set(self, project: Project):
        project.write("manifest.yaml", yaml.safe_dump({"metadata": {"title": "T"}, "pages": ["text/ch1.md"]}))

        assert Book.load_from_file(project.manifest_path).name == project.root.name

    def test_derived_name_is_slugified(self, tmp_path: Path):
        root = tmp_path / "My Book! (draft)"
        root.mkdir()
        (root / "text").mkdir()
        (root / "text" / "ch1.md").write_text("# Hi\n")
        (root / "manifest.yaml").write_text(
            yaml.safe_dump({"metadata": {"title": "T"}, "pages": ["text/ch1.md"]})
        )

        from md2epub.core.environment import setup_environment

        setup_environment("md2epub-test", version="0.0.0").set_work_dir(root)
        book = Book.load_from_file(root / "manifest.yaml")

        assert book.name == "My-Book-draft"


# region Config.include_file


class TestConfigIncludeFile:
    def test_valid_relative_include_is_merged(self, project: Project, env: Environment):
        env.set_work_dir(project.root)
        project.write("shared-config.yaml", yaml.safe_dump({"markdown": {"tab_length": 8}}))
        project.manifest(book={"config": {"include_file": "shared-config.yaml"}})

        assert Book.load_from_file(project.manifest_path).config.markdown.tab_length == 8

    def test_config_include_file_cannot_escape_the_project(self, project: Project, env: Environment, outside: Path):
        env.set_work_dir(project.root)
        (outside / "config.yaml").write_text(yaml.safe_dump({"markdown": {"tab_length": 999}}))
        project.manifest(book={"config": {"include_file": str(outside / "config.yaml")}})

        with pytest.raises(ValidationError):
            Book.load_from_file(project.manifest_path)

    def test_config_include_file_relative_escape_is_rejected(self, project: Project, env: Environment, outside: Path):
        env.set_work_dir(project.root)
        (outside / "config.yaml").write_text(yaml.safe_dump({"markdown": {"tab_length": 999}}))
        project.manifest(book={"config": {"include_file": "../outside/config.yaml"}})

        with pytest.raises(ValidationError):
            Book.load_from_file(project.manifest_path)
