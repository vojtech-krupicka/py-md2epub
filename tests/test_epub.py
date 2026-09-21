"""The EPUB zip writer (`Epub`) and the file models (`EpubFile` and friends)."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest
from pydantic import ValidationError

from md2epub.types.epub import Epub
from md2epub.types.epub_content import CssFile, EpubFile, HtmlFile, NcxFile, OpfFile

# region Epub writer


class TestEpubWriter:
    def test_text_and_file_roundtrip(self, tmp_path: Path):
        source = tmp_path / "data.bin"
        source.write_bytes(b"\x00\x01binary")
        target = tmp_path / "book.epub"

        epub = Epub()
        epub.add_text("héllo", "OEBPS/a.txt")
        epub.add_file(source, Path("OEBPS/data.bin"))
        epub.save(target)

        with zipfile.ZipFile(target) as z:
            assert z.read("OEBPS/a.txt").decode("utf-8") == "héllo"
            assert z.read("OEBPS/data.bin") == b"\x00\x01binary"

    def test_entries_keep_insertion_order_and_mimetype_is_stored(self, tmp_path: Path):
        epub = Epub()
        epub.add_text("application/epub+zip", "mimetype")
        epub.add_text("<x/>", "META-INF/container.xml")
        epub.save(tmp_path / "book.epub")

        with zipfile.ZipFile(tmp_path / "book.epub") as z:
            first = z.infolist()[0]
            assert first.filename == "mimetype"
            # EPUB (OCF) requires the mimetype entry to be the first one and not compressed.
            assert first.compress_type == zipfile.ZIP_STORED
            assert z.namelist() == ["mimetype", "META-INF/container.xml"]

    def test_missing_source_file(self, tmp_path: Path):
        with pytest.raises(RuntimeError, match="not exists"):
            Epub().add_file(tmp_path / "nope.png", "OEBPS/nope.png")

    @pytest.mark.parametrize("name", ["OEBPS/../../evil.txt", "../evil.txt", "/etc/evil.txt"])
    # @pytest.mark.xfail(
    #     strict=True, reason="`Epub.add` writes any entry name, including `..` and absolute names (zip-slip)"
    # )
    def test_unsafe_entry_names_are_rejected(self, name: str):
        with pytest.raises((ValueError, RuntimeError)):
            Epub().add_text("x", name)

    @pytest.mark.filterwarnings("ignore:Duplicate name")
    @pytest.mark.xfail(
        strict=True, reason="`Epub.add` appends a second entry with the same name, `zipfile` only warns about it"
    )
    def test_duplicate_entry_names_are_rejected(self):
        epub = Epub()
        epub.add_text("first", "OEBPS/page.xhtml")

        with pytest.raises((ValueError, RuntimeError), match=r"page\.xhtml"):
            epub.add_text("second", "OEBPS/page.xhtml")

    def test_same_content_under_different_names_is_fine(self, tmp_path: Path):
        epub = Epub()
        epub.add_text("same", "OEBPS/a.xhtml")
        epub.add_text("same", "OEBPS/b.xhtml")
        epub.save(tmp_path / "book.epub")

        assert zipfile.ZipFile(tmp_path / "book.epub").namelist() == ["OEBPS/a.xhtml", "OEBPS/b.xhtml"]


# region EpubFile models


class TestEpubFile:
    @pytest.mark.parametrize(
        ("name", "class_name", "mimetype"),
        [
            ("a.css", "CssFile", "text/css"),
            ("a.png", "ImageFile", "image/png"),
            ("a.jpg", "ImageFile", "image/jpeg"),
            ("a.jpeg", "ImageFile", "image/jpeg"),
            ("a.gif", "ImageFile", "image/gif"),
            ("a.svg", "ImageFile", "image/svg+xml"),
            ("a.otf", "FontFile", "application/x-font-opentype"),
            ("a.xhtml", "HtmlFile", "application/xhtml+xml"),
            ("a.bin", "EpubFile", "application/octet-stream"),
        ],
    )
    def test_file_kind_and_mimetype_follow_the_suffix(self, tmp_path: Path, name: str, class_name: str, mimetype: str):
        file = EpubFile.create_from_source(tmp_path / name)

        assert type(file).__name__ == class_name
        assert file.mimetype == mimetype

    def test_destination_and_href_are_relative_to_the_work_dir(self, tmp_path: Path):
        file = EpubFile.create_from_source(tmp_path / "images" / "cover.png")

        assert file.dest == Path("OEBPS/images/cover.png")
        assert file.href == "images/cover.png"

    def test_files_with_the_same_name_get_different_ids(self, tmp_path: Path):
        a = EpubFile.create_from_source(tmp_path / "a" / "x.png")
        b = EpubFile.create_from_source(tmp_path / "b" / "x.png")

        assert a.unique_id != b.unique_id

    def test_wrong_suffix_for_a_specific_file_kind(self, tmp_path: Path):
        with pytest.raises((RuntimeError, ValidationError)):
            CssFile(source=tmp_path / "a.png")

    def test_html_file(self, tmp_path: Path):
        file = HtmlFile(source=tmp_path / "text" / "ch1.xhtml", content="<html/>")

        assert file.dest == Path("OEBPS/text/ch1.xhtml")

    def test_special_files_live_at_the_epub_root(self):
        assert OpfFile(content="").dest == Path("OEBPS/content.opf")
        assert NcxFile(content="").dest == Path("OEBPS/toc.ncx")
        assert NcxFile(content="").unique_id == "ncx"

    @pytest.mark.xfail(
        strict=True,
        reason="`.txt`/`.xml` files become `TextFile`, whose `content` is never read from the source: copied empty",
    )
    @pytest.mark.parametrize("name", ["notes.txt", "meta.xml"])
    def test_text_files_keep_their_content_when_copied(self, tmp_path: Path, name: str):
        (tmp_path / name).write_text("important\n", encoding="utf-8")
        epub = Epub()

        EpubFile.create_from_source(tmp_path / name).add_to_epub(epub)
        epub.save(tmp_path / "book.epub")

        assert zipfile.ZipFile(tmp_path / "book.epub").read(f"OEBPS/{name}") == b"important\n"
