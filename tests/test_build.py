"""End-to-end: build a real project with the real `build` command and inspect the resulting EPUB."""

from __future__ import annotations

import posixpath
import re
import zipfile
from pathlib import Path

import pytest

from md2epub.commands import build
from tests.conftest import Project
from tests.helpers import NS, xml, xml_errors

FULL_BOOK = {
    "pages": [
        {"type": "cover", "cover_image": "images/cover.png"},
        {"type": "title"},
        {"type": "toc"},
        "text/ch1.md",
    ],
    "stylesheets": ["styles/s.css"],
}


@pytest.fixture
def epub(project: Project) -> zipfile.ZipFile:
    """The default project, built."""
    return zipfile.ZipFile(project.build())


@pytest.fixture
def full_epub(project: Project) -> zipfile.ZipFile:
    """A project using every kind of default page, built."""
    project.manifest(book=FULL_BOOK)
    return zipfile.ZipFile(project.build())


# region Structure


class TestStructure:
    def test_build_creates_the_file(self, project: Project):
        out = project.build()

        assert out.is_file()
        assert zipfile.is_zipfile(out)

    def test_mimetype_is_the_first_entry_and_stored(self, epub: zipfile.ZipFile):
        first = epub.infolist()[0]

        assert first.filename == "mimetype"
        assert first.compress_type == zipfile.ZIP_STORED
        assert epub.read("mimetype") == b"application/epub+zip"

    def test_required_parts_exist(self, epub: zipfile.ZipFile):
        assert {"mimetype", "META-INF/container.xml", "OEBPS/content.opf", "OEBPS/toc.ncx"} <= set(epub.namelist())

    def test_container_points_to_the_opf(self, epub: zipfile.ZipFile):
        root = xml(epub, "META-INF/container.xml")
        (rootfile,) = root.xpath("//*[local-name()='rootfile']")

        assert rootfile.get("full-path") == "OEBPS/content.opf"

    def test_all_xml_parts_are_well_formed(self, full_epub: zipfile.ZipFile):
        assert xml_errors(full_epub) == {}

    def test_no_duplicate_entries(self, full_epub: zipfile.ZipFile):
        names = full_epub.namelist()

        assert len(names) == len(set(names))

    def test_sources_are_copied_next_to_their_project_paths(self, full_epub: zipfile.ZipFile):
        names = set(full_epub.namelist())

        assert "OEBPS/images/cover.png" in names
        assert "OEBPS/styles/s.css" in names
        assert "OEBPS/text/ch1.xhtml" in names

    def test_every_entry_is_listed_in_the_opf_manifest(self, full_epub: zipfile.ZipFile):
        opf = xml(full_epub, "OEBPS/content.opf")
        listed = set(opf.xpath("//opf:manifest/opf:item/@href", namespaces=NS))
        shipped = {n.removeprefix("OEBPS/") for n in full_epub.namelist() if n.startswith("OEBPS/")} - {"content.opf"}

        assert listed == shipped

    def test_spine_and_guide(self, full_epub: zipfile.ZipFile):
        opf = xml(full_epub, "OEBPS/content.opf")

        assert len(opf.xpath("//opf:spine/opf:itemref", namespaces=NS)) == 4
        assert opf.xpath("//opf:guide/opf:reference/@type", namespaces=NS) == ["cover", "title-page", "toc"]
        assert opf.xpath("//opf:spine/@toc", namespaces=NS) == ["ncx"]

    def test_toc_page_links_to_the_chapter(self, project: Project):
        epub = zipfile.ZipFile(project.build())
        toc = xml(epub, "OEBPS/content/toc.xhtml")

        assert any("ch1.xhtml" in href for href in toc.xpath("//x:a/@href", namespaces=NS))

    def test_ncx_lists_the_chapter(self, project: Project):
        epub = zipfile.ZipFile(project.build())
        ncx = xml(epub, "OEBPS/toc.ncx")
        sources = ncx.xpath("//ncx:navPoint/ncx:content/@src", namespaces=NS)

        assert any("ch1.xhtml" in src for src in sources)

    def test_generated_sub_book_pages_live_in_their_own_folder(self, project: Project):
        project.manifest(
            book={
                "pages": [
                    {"type": "toc"},
                    {
                        "type": "book",
                        "book": {"name": "part1", "title": "Part One", "pages": [{"type": "toc"}, "text/ch1.md"]},
                    },
                ]
            }
        )
        names = set(zipfile.ZipFile(project.build()).namelist())

        assert "OEBPS/content/part1/toc.xhtml" in names  # generated pages: <book>/<page name>.xhtml
        assert "OEBPS/text/ch1.xhtml" in names  # chapters keep the folder of their source

    def test_sub_book_heading_is_not_a_dead_link(self, project: Project):
        """A sub-book's heading groups its children; it must still be a working link, not `href=""`."""
        project.manifest(
            book={
                "pages": [
                    {"type": "toc"},
                    {
                        "type": "book",
                        "book": {"name": "part1", "title": "Part One", "pages": [{"type": "toc"}, "text/ch1.md"]},
                    },
                ]
            }
        )
        epub = zipfile.ZipFile(project.build())
        toc = xml(epub, "OEBPS/content/toc.xhtml")
        ncx = xml(epub, "OEBPS/toc.ncx")

        toc_hrefs = toc.xpath("//x:a/@href", namespaces=NS)
        ncx_srcs = ncx.xpath("//ncx:navPoint/ncx:content/@src", namespaces=NS)

        # Nothing should be empty, and everything non-empty should resolve to a real entry in the EPUB.
        assert "" not in toc_hrefs
        assert "" not in ncx_srcs
        for href in toc_hrefs:
            target = posixpath.normpath(
                posixpath.join(posixpath.dirname("OEBPS/content/toc.xhtml"), href.split("#")[0])
            )
            assert target in epub.namelist(), href
        for src in ncx_srcs:
            target = posixpath.normpath(posixpath.join("OEBPS", src.split("#")[0]))
            assert target in epub.namelist(), src

        # The heading itself, and its child chapter, must still be reachable as text somewhere on the page.
        assert "Part One" in " ".join(toc.xpath("//text()"))

    def test_chapter_toc_title_overrides_the_heading(self, project: Project):
        """`toc_title` overrides the table-of-contents label only, not the chapter's own <title>."""
        project.write("text/ch1.md", "# Real Heading\n\nBody.\n")
        project.manifest(
            book={
                "pages": [
                    {"type": "toc"},
                    {"type": "chapter", "source": "text/ch1.md", "toc_title": "Custom Label"},
                ]
            }
        )

        epub = zipfile.ZipFile(project.build())
        toc = xml(epub, "OEBPS/content/toc.xhtml")
        ncx = xml(epub, "OEBPS/toc.ncx")
        chapter = xml(epub, "OEBPS/text/ch1.xhtml")

        assert toc.xpath("//x:a/text()", namespaces=NS) == ["Custom Label"]
        assert ncx.xpath("//ncx:navLabel/ncx:text/text()", namespaces=NS) == ["Custom Label"]
        assert chapter.xpath("string(//x:title)", namespaces=NS) == "Real Heading"

    def test_page_toc_title_overrides_the_default_label(self, project: Project):
        """A page that has no heading of its own (a custom page) falls back to its `name`; `toc_title` overrides it."""
        template = project.write(
            "page.jinja", '<html xmlns="http://www.w3.org/1999/xhtml"><body><p>hi</p></body></html>'
        )
        project.manifest(
            book={
                "pages": [
                    {"type": "toc"},
                    {
                        "type": "custom",
                        "name": "extras",
                        "template": str(template),
                        "add_to_toc": True,
                        "toc_title": "Bonus Material",
                    },
                    "text/ch1.md",
                ]
            }
        )

        epub = zipfile.ZipFile(project.build())
        toc = xml(epub, "OEBPS/content/toc.xhtml")

        assert "Bonus Material" in toc.xpath("//x:a/text()", namespaces=NS)
        assert "extras" not in " ".join(toc.xpath("//text()"))

    def test_sub_book_toc_title_overrides_the_book_title(self, project: Project):
        """A sub-book's `toc_title` overrides its own heading in the parent's table of contents."""
        project.manifest(
            book={
                "pages": [
                    {"type": "toc"},
                    {
                        "type": "book",
                        "book": {
                            "name": "part1",
                            "title": "The Real, Long Title Of This Part",
                            "toc_title": "Part One",
                            "pages": [{"type": "toc"}, "text/ch1.md"],
                        },
                    },
                ]
            }
        )

        epub = zipfile.ZipFile(project.build())
        text = " ".join(xml(epub, "OEBPS/content/toc.xhtml").xpath("//text()"))

        assert "Part One" in text
        assert "The Real, Long Title Of This Part" not in text


# region Metadata


class TestMetadata:
    def test_title_author_and_language(self, epub: zipfile.ZipFile):
        opf = xml(epub, "OEBPS/content.opf")

        assert opf.xpath("//dc:title/text()", namespaces=NS) == ["Test Book"]
        assert opf.xpath("//dc:creator/text()", namespaces=NS) == ["Jane Doe"]
        assert opf.xpath("//dc:language/text()", namespaces=NS) == ["en"]

    def test_unique_identifier_is_declared(self, epub: zipfile.ZipFile):
        opf = xml(epub, "OEBPS/content.opf")
        ident = opf.get("unique-identifier")

        assert opf.xpath(f"//dc:identifier[@id='{ident}']", namespaces=NS)

    def test_ncx_uid_matches_the_opf_identifier(self, epub: zipfile.ZipFile):
        opf = xml(epub, "OEBPS/content.opf")
        ncx = xml(epub, "OEBPS/toc.ncx")
        (uid,) = opf.xpath("//dc:identifier[@id]/text()", namespaces=NS)

        assert ncx.xpath("//ncx:meta[@name='dtb:uid']/@content", namespaces=NS) == [uid]

    def test_book_id_is_stable_across_rebuilds(self, project: Project):
        """Two builds of the same, unchanged project must produce the same book identifier."""
        first = xml(zipfile.ZipFile(project.build(project.out_dir / "a.epub")), "OEBPS/content.opf")
        second = xml(zipfile.ZipFile(project.build(project.out_dir / "b.epub")), "OEBPS/content.opf")

        identifier = "string(//dc:identifier[@id])"
        assert first.xpath(identifier, namespaces=NS) == second.xpath(identifier, namespaces=NS)

    def test_dates_are_filled(self, epub: zipfile.ZipFile):
        opf = xml(epub, "OEBPS/content.opf")
        dates = opf.xpath("//dc:date/text()", namespaces=NS)

        assert len(dates) == 3
        assert all(re.fullmatch(r"\d{4}(-\d{2}-\d{2})?", d) for d in dates)

    def test_contributors_produce_well_formed_xml(self, project: Project):
        project.manifest(contributors=[{"name": "Ed Itor", "role": "edt"}])
        epub = zipfile.ZipFile(project.build())

        assert xml_errors(epub) == {}
        assert xml(epub, "OEBPS/content.opf").xpath("//dc:contributor/text()", namespaces=NS) == ["Ed Itor"]

    def test_ampersand_in_the_title_is_escaped(self, project: Project):
        project.manifest(title="Tom & Jerry", book=FULL_BOOK)
        epub = zipfile.ZipFile(project.build())

        assert xml_errors(epub) == {}
        assert xml(epub, "OEBPS/content.opf").xpath("//dc:title/text()", namespaces=NS) == ["Tom & Jerry"]

    def test_metadata_cannot_inject_xml_elements(self, project: Project):
        project.manifest(title='X</dc:title><dc:creator opf:role="aut">FORGED</dc:creator><dc:title>')
        epub = zipfile.ZipFile(project.build())
        creators = xml(epub, "OEBPS/content.opf").xpath("//dc:creator/text()", namespaces=NS)

        assert creators == ["Jane Doe"]


# region Content


class TestContent:
    def test_chapter_text_is_present(self, epub: zipfile.ZipFile):
        assert "Hello" in epub.read("OEBPS/text/ch1.xhtml").decode("utf-8")

    def test_chapter_markup_is_present(self, epub: zipfile.ZipFile):
        chapter = xml(epub, "OEBPS/text/ch1.xhtml")

        assert chapter.xpath("//x:h1/text()", namespaces=NS) == ["Chapter One"]
        assert chapter.xpath("//x:em/text()", namespaces=NS) == ["world"]

    def test_chapter_text_is_clean(self, epub: zipfile.ZipFile):
        chapter = xml(epub, "OEBPS/text/ch1.xhtml")
        text = "".join(chapter.xpath("//x:body//text()", namespaces=NS)).strip()

        assert not text.startswith("b'")
        assert "\\x" not in text
        assert "\u201equotes\u201c" in text  # Czech smart quotes from the default `smarty` config

    def test_stylesheet_is_linked_from_the_chapter(self, project: Project):
        project.manifest(book={"stylesheets": ["styles/s.css"]})
        chapter = xml(zipfile.ZipFile(project.build()), "OEBPS/text/ch1.xhtml")

        assert chapter.xpath("//x:link[@rel='stylesheet']/@href", namespaces=NS) == ["../styles/s.css"]

    def test_cover_page_references_its_image(self, full_epub: zipfile.ZipFile):
        cover = xml(full_epub, "OEBPS/content/cover.xhtml")

        assert cover.xpath("//x:img/@src", namespaces=NS) == ["../images/cover.png"]

    def test_custom_page_is_rendered_from_a_template(self, project: Project):
        template = project.write(
            "tpl.jinja", '<html xmlns="http://www.w3.org/1999/xhtml"><body><p>{{ values.greeting }}</p></body></html>'
        )
        project.manifest(
            book={
                "pages": [
                    {"type": "toc"},
                    {"type": "custom", "name": "hello", "template": str(template), "values": {"greeting": "hi there"}},
                ]
            }
        )
        page = xml(zipfile.ZipFile(project.build()), "OEBPS/content/hello.xhtml")

        assert page.xpath("//x:p/text()", namespaces=NS) == ["hi there"]

    def test_custom_template_path_is_relative_to_the_manifest(
        self, project: Project, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ):
        project.write("tpl.jinja", '<html xmlns="http://www.w3.org/1999/xhtml"><body>ok</body></html>')
        project.manifest(
            book={"pages": [{"type": "toc"}, {"type": "custom", "name": "hello", "template": "tpl.jinja"}]}
        )
        monkeypatch.chdir(tmp_path)  # run from somewhere else than the project folder

        assert "OEBPS/content/hello.xhtml" in zipfile.ZipFile(project.build()).namelist()

    def test_opf_ids_are_valid_xml_ids(self, project: Project):
        project.write("text/01-intro.md", "# Intro\n")
        project.manifest(book={"pages": [{"type": "toc"}, "text/01-intro.md"]})
        opf = xml(zipfile.ZipFile(project.build()), "OEBPS/content.opf")
        ids = opf.xpath("//opf:manifest/opf:item/@id", namespaces=NS)

        assert ids
        assert all(re.fullmatch(r"[A-Za-z_][\w.\-]*", i) for i in ids)

    def test_hrefs_are_url_encoded(self, project: Project):
        project.write("text/my chapter.md", "# Spaces\n")
        project.manifest(book={"pages": [{"type": "toc"}, "text/my chapter.md"]})
        opf = xml(zipfile.ZipFile(project.build()), "OEBPS/content.opf")

        assert not any(" " in href for href in opf.xpath("//opf:item/@href", namespaces=NS))


# region Command behaviour


class TestBuildCommand:
    def test_existing_output_is_protected(self, project: Project):
        out = project.build()

        with pytest.raises(FileExistsError):
            build.run(project.manifest_path, out, overwrite=False)

    def test_overwrite_replaces_the_output(self, project: Project):
        out = project.build()
        out.write_bytes(b"old")

        build.run(project.manifest_path, out, overwrite=True)

        assert zipfile.is_zipfile(out)

    def test_default_output_is_created_next_to_the_manifest(self, project: Project):
        build.run(project.manifest_path, None, overwrite=False)

        assert (project.root / "proj.epub").is_file()

    def test_book_without_a_toc_page_fails_with_a_clear_error(self, project: Project):
        project.manifest(book={"pages": ["text/ch1.md"]})

        with pytest.raises(RuntimeError, match="TOC"):
            project.build()

    def test_missing_chapter_source_fails(self, project: Project):
        project.manifest(book={"pages": [{"type": "toc"}, "text/missing.md"]})

        with pytest.raises(FileNotFoundError):
            project.build()
