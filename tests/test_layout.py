"""
Where every file ends up inside the EPUB, and what happens when two files want the same place.

The rules these tests describe:

- Anything that has a source file keeps its folder: a file's location inside the EPUB is its path relative to the
  manifest folder (`text/ch1.md` -> `OEBPS/text/ch1.xhtml`, like `images/cover.png` -> `OEBPS/images/cover.png`).
  Because of that, relative links inside a chapter (images, stylesheets) keep working unchanged.
- Pages without a source file (cover, title, toc, custom) live in `OEBPS/<book>/<page name>.xhtml`.
- Two different files must never be written to the same place: that is an error, not a silent overwrite.
- The same source file listed twice is written once.

Tests marked `xfail(strict=True)` describe behaviour that is not implemented yet, see `test_security.py`.
"""

from __future__ import annotations

import posixpath
import zipfile
from collections import Counter

import pytest

from tests.conftest import Project
from tests.helpers import NS, PNG_1X1, xml

NO_COLLISION_CHECK = pytest.mark.xfail(
    strict=True, reason="nothing checks that two files map to the same destination, the zip only warns"
)
# Today's zipfile only warns about a duplicate entry, which is noise in the expected-to-fail runs.
DUPLICATE_WARNING = pytest.mark.filterwarnings("ignore:Duplicate name")

PAGE = '<html xmlns="http://www.w3.org/1999/xhtml"><body><p>generated</p></body></html>'


def duplicates(epub: zipfile.ZipFile) -> list[str]:
    return [name for name, count in Counter(epub.namelist()).items() if count > 1]


# region Chapters keep their folder


@pytest.mark.parametrize(
    ("source", "entry"),
    [
        ("text/ch1.md", "OEBPS/text/ch1.xhtml"),
        ("intro.md", "OEBPS/intro.xhtml"),
        ("part1/chapter.01.md", "OEBPS/part1/chapter.01.xhtml"),
        ("a/b/c.md", "OEBPS/a/b/c.xhtml"),
    ],
)
def test_chapter_keeps_its_folder(project: Project, source: str, entry: str):
    project.write(source, "# Title\n")
    project.manifest(book={"pages": [{"type": "toc"}, source]})

    assert entry in zipfile.ZipFile(project.build()).namelist()


@DUPLICATE_WARNING
def test_chapters_with_the_same_file_name_in_different_folders_do_not_collide(project: Project):
    project.write("part1/intro.md", "# Intro of part 1\n")
    project.write("part2/intro.md", "# Intro of part 2\n")
    project.manifest(book={"pages": [{"type": "toc"}, "part1/intro.md", "part2/intro.md"]})

    epub = zipfile.ZipFile(project.build())
    text = " ".join(epub.read(name).decode("utf-8") for name in set(epub.namelist()) if name.endswith(".xhtml"))

    assert duplicates(epub) == []
    assert "Intro of part 1" in text
    assert "Intro of part 2" in text


def test_stylesheets_with_the_same_file_name_in_different_folders_do_not_collide(project: Project):
    """Control test: assets already keep their folder, this is the behaviour chapters should follow."""
    project.write("styles01/styles.css", "a {}")
    project.write("styles02/styles.css", "b {}")
    project.manifest(book={"files": ["styles01", "styles02"]})

    epub = zipfile.ZipFile(project.build())

    assert {"OEBPS/styles01/styles.css", "OEBPS/styles02/styles.css"} <= set(epub.namelist())
    assert duplicates(epub) == []


def test_relative_links_in_a_chapter_still_resolve(project: Project):
    """`![](../../images/pic.png)` is right on disk (text/sub/deep.md), so it must be right inside the EPUB too."""
    project.write("images/pic.png", PNG_1X1)
    project.write("text/sub/deep.md", "# Deep\n\n![pic](../../images/pic.png)\n")
    project.manifest(book={"files": ["images"], "pages": [{"type": "toc"}, "text/sub/deep.md"]})

    epub = zipfile.ZipFile(project.build())
    (chapter,) = [name for name in epub.namelist() if name.endswith("deep.xhtml")]
    (src,) = xml(epub, chapter).xpath("//x:img/@src", namespaces=NS)

    assert posixpath.normpath(posixpath.join(posixpath.dirname(chapter), src)) in epub.namelist()


WRONG_DEPTH = pytest.mark.xfail(
    strict=True, reason="`prepare()` builds stylesheet hrefs against the old `content/` folder, not the chapter's own"
)


@pytest.mark.parametrize(
    "source",
    [
        pytest.param("top.md", marks=WRONG_DEPTH),
        "text/one.md",  # same depth as the old `content/` folder, so it happens to be right
        pytest.param("text/sub/deep.md", marks=WRONG_DEPTH),
        pytest.param("a/b/c/d.md", marks=WRONG_DEPTH),
    ],
)
def test_stylesheet_links_in_a_chapter_resolve_from_any_depth(project: Project, source: str):
    project.write(source, "# Title\n")
    project.manifest(book={"stylesheets": ["styles/s.css"], "pages": [{"type": "toc"}, source]})

    epub = zipfile.ZipFile(project.build())
    (chapter,) = [name for name in epub.namelist() if name.endswith(source.replace(".md", ".xhtml"))]
    (href,) = xml(epub, chapter).xpath("//x:link[@rel='stylesheet']/@href", namespaces=NS)

    assert posixpath.normpath(posixpath.join(posixpath.dirname(chapter), href)) == "OEBPS/styles/s.css"


# region Two different files, one destination


@NO_COLLISION_CHECK
@DUPLICATE_WARNING
def test_two_pages_with_the_same_name_are_refused(project: Project):
    template = project.write("page.jinja", PAGE)
    project.manifest(
        book={
            "pages": [
                {"type": "toc"},
                {"type": "custom", "name": "same", "template": str(template)},
                {"type": "custom", "name": "same", "template": str(template)},
                "text/ch1.md",
            ]
        }
    )

    with pytest.raises((ValueError, RuntimeError), match=r"same\.xhtml"):
        project.build()


@NO_COLLISION_CHECK
@DUPLICATE_WARNING
def test_a_chapter_cannot_overwrite_a_generated_page(project: Project):
    """A source `content/toc.md` and the toc page (`content/toc.xhtml`) want the same destination."""
    project.write("content/toc.md", "# Not the table of contents\n")
    project.manifest(book={"pages": [{"type": "toc"}, "content/toc.md"]})

    with pytest.raises((ValueError, RuntimeError), match=r"toc\.xhtml"):
        project.build()


# region The same source listed twice is written once

SAME_SOURCE_TWICE = {
    "stylesheet-in-book-and-page": {
        "stylesheets": ["styles/s.css"],
        "pages": [{"type": "toc"}, {"type": "chapter", "source": "text/ch1.md", "stylesheets": ["styles/s.css"]}],
    },
    "folder-and-cover-image-inside-it": {
        "files": ["images"],
        "pages": [{"type": "toc"}, {"type": "cover", "cover_image": "images/cover.png"}, "text/ch1.md"],
    },
    "folder-and-stylesheet-inside-it": {
        "files": ["styles"],
        "stylesheets": ["styles/s.css"],
        "pages": [{"type": "toc"}, "text/ch1.md"],
    },
}


@NO_COLLISION_CHECK
@DUPLICATE_WARNING
@pytest.mark.parametrize("case", SAME_SOURCE_TWICE)
def test_the_same_source_file_is_written_once(project: Project, case: str):
    project.manifest(book=SAME_SOURCE_TWICE[case])

    epub = zipfile.ZipFile(project.build())
    hrefs = xml(epub, "OEBPS/content.opf").xpath("//opf:manifest/opf:item/@href", namespaces=NS)

    assert duplicates(epub) == []
    assert len(hrefs) == len(set(hrefs))
