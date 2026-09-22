"""
Security regression tests.

Every test describes what a *safe* build looks like: it either refuses a hostile input, or it builds
without leaking anything. Refusing is always fine, see `build_or_refuse()`.

Tests marked `xfail(strict=True)` reproduce problems that are known but not fixed yet. They are expected
to fail today. Once a problem is fixed, pytest reports the test as XPASS(strict), which counts as a
failure - that is the cue to delete the marker and keep the test as a regression guard.

The exploits only ever touch files below pytest's `tmp_path`.
"""

from __future__ import annotations

import sys
import zipfile
from collections.abc import Callable
from pathlib import Path

import pytest
from pydantic import ValidationError

from md2epub.commands import build
from md2epub.models.public.manifest import Manifest
from tests.conftest import Project
from tests.helpers import build_or_refuse, leaks

KNOWN = pytest.mark.xfail(strict=True)

# region Paths from the manifest must stay inside the project


def _book(pages=(), **extra) -> dict:
    return {"pages": [{"type": "toc"}, *pages], **extra}


# id -> (builds the `book` part of the manifest from a dict of references to the outside files, known bug?)
ESCAPES: dict[str, tuple[Callable[[dict], dict], bool]] = {
    "chapter-relative": (lambda r: _book([{"type": "chapter", "source": r["md_rel"]}]), False),
    "chapter-absolute": (lambda r: _book([{"type": "chapter", "source": r["md_abs"]}]), False),
    "cover-relative": (lambda r: _book([{"type": "cover", "cover_image": r["png_rel"]}]), False),
    "cover-absolute": (lambda r: _book([{"type": "cover", "cover_image": r["png_abs"]}]), False),
    "stylesheet-relative": (lambda r: _book(["text/ch1.md"], stylesheets=[r["css_rel"]]), False),
    "stylesheet-absolute": (lambda r: _book(["text/ch1.md"], stylesheets=[r["css_abs"]]), False),
    "files-parent-directory": (lambda r: _book(["text/ch1.md"], files=[".."]), False),
}


@pytest.mark.parametrize(
    "case",
    [pytest.param(name, marks=KNOWN if known else ()) for name, (_, known) in ESCAPES.items()],
)
def test_manifest_paths_cannot_escape_the_project(project: Project, outside: Path, case: str):
    refs = {
        "md_rel": "../outside/secret.md",
        "png_rel": "../outside/secret.png",
        "css_rel": "../outside/secret.css",
        "md_abs": str(outside / "secret.md"),
        "png_abs": str(outside / "secret.png"),
        "css_abs": str(outside / "secret.css"),
    }
    project.manifest(book=ESCAPES[case][0](refs))

    epub = build_or_refuse(project)

    if epub is not None:
        assert leaks(epub) == []


def test_project_files_inside_the_project_still_build(project: Project):
    """Control test: the same manifest shapes as above, but pointing inside the project, must work."""
    project.write("assets/logo.png", b"logo")
    project.manifest(
        book=_book(
            [{"type": "cover", "cover_image": "images/cover.png"}, "text/ch1.md"],
            stylesheets=["styles/s.css"],
            files=["assets"],
        )
    )

    epub = build_or_refuse(project)

    assert epub is not None
    assert "OEBPS/assets/logo.png" in epub.namelist()
    assert leaks(epub) == []


def test_page_name_cannot_traverse(project: Project):
    project.manifest(book=_book([{"type": "chapter", "name": "../../../evil", "source": "text/ch1.md"}]))

    epub = build_or_refuse(project)

    if epub is not None:
        assert leaks(epub) == []


def test_symlink_cannot_escape_the_project(project: Project, outside: Path):
    link = project.root / "images" / "innocent.png"
    try:
        link.symlink_to(outside / "secret.png")
    except OSError:
        pytest.skip("symlinks are not supported here")
    project.manifest(book=_book([{"type": "cover", "cover_image": "images/innocent.png"}, "text/ch1.md"]))

    epub = build_or_refuse(project)

    if epub is not None:
        assert leaks(epub) == []


# region A manifest must not be able to run code


def test_custom_template_cannot_execute_code(project: Project, tmp_path: Path):
    marker = tmp_path / "pwned_by_template"
    template = project.write(
        "evil.jinja", "{{ cycler.__init__.__globals__.os.popen('touch " + str(marker) + "').read() }}"
    )
    project.manifest(book=_book([{"type": "custom", "name": "evil", "template": str(template)}]))

    build_or_refuse(project)

    assert not marker.exists()


def test_markdown_extension_cannot_import_arbitrary_modules(
    project: Project, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    marker = tmp_path / "pwned_by_extension"
    name = "md2epub_test_evil_extension"
    project.write(
        f"{name}.py",
        "import pathlib\n"
        f"pathlib.Path({str(marker)!r}).write_text('import-time code ran')\n"
        "from markdown import Extension\n"
        "def makeExtension(**kwargs):\n"
        "    return Extension(**kwargs)\n",
    )
    # `python -m md2epub` puts the current directory (the project folder) on sys.path
    monkeypatch.syspath_prepend(str(project.root))
    project.manifest(config={"markdown": {"additional_extensions": [name]}})

    try:
        build_or_refuse(project)
    finally:
        sys.modules.pop(name, None)

    assert not marker.exists()


def test_builtin_and_md2epub_extensions_load_without_any_flag(project: Project):
    """Control test: the allowlist must not get in the way of what a manifest is actually meant to use."""
    project.write("text/ch1.md", "Šel k lesu.")  # exercises the `vlna` extension (a non-breaking space after `k`)
    project.manifest(
        config={"markdown": {"additional_extensions": ["toc", "md2epub.extensions.vlna"]}},
        book=_book(["text/ch1.md"]),
    )

    epub = build_or_refuse(project)

    assert epub is not None


@KNOWN
def test_markdown_extension_is_allowed_with_explicit_trust(
    project: Project, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    """The opt-in is a decision made by whoever runs the build, not something the manifest can grant itself."""
    marker = tmp_path / "extension_ran"
    name = "md2epub_test_harmless_extension"
    project.write(
        f"{name}.py",
        "import pathlib\n"
        f"pathlib.Path({str(marker)!r}).write_text('ran')\n"
        "from markdown import Extension\n"
        "class E(Extension):\n"
        "    def extendMarkdown(self, md):\n"
        "        pass\n"
        "def makeExtension(**kwargs):\n"
        "    return E(**kwargs)\n",
    )
    monkeypatch.syspath_prepend(str(project.root))
    project.manifest(config={"markdown": {"additional_extensions": [name]}})

    try:
        project.build(trust_extensions=True)
    finally:
        sys.modules.pop(name, None)

    assert marker.exists()


# region The manifest must not control where the output goes


def test_epub_suffix_cannot_redirect_the_output(project: Project, tmp_path: Path):
    # A folder named like the manifest lets `<name>/../..` resolve, the way a hostile project would ship it.
    (project.root / "book").mkdir()
    project.manifest(filename="book.yaml", config={"epub": {"epub_suffix": "/../../pwned.txt"}})

    try:
        build.run(project.manifest_path, None, True)
    except Exception:
        pass  # refusing is fine

    assert not (tmp_path / "pwned.txt").exists()


def test_output_stays_next_to_the_manifest_by_default(project: Project):
    build.run(project.manifest_path, None, True)

    assert [p.name for p in project.root.glob("*.epub")] == ["proj.epub"]
    assert zipfile.is_zipfile(project.root / "proj.epub")


# region Names become file and folder names inside the EPUB

# `name` of a book, sub-book or page ends up in a path (`content/<book>/<page>.xhtml`), so it must never be able to
# point somewhere else. The model allows `[A-Za-z0-9._-]` but not a name made of dots only.
DANGEROUS_NAMES = [".", "..", "...", "../x", "x/..", "a/b", "/abs", "a\\b", "", "a b"]


def _chapter_named(name: str) -> dict:
    return _book([{"type": "chapter", "name": name, "source": "text/ch1.md"}])


def _toc_named(name: str) -> dict:
    return {"pages": [{"type": "toc", "name": name}, "text/ch1.md"]}


def _book_named(name: str) -> dict:
    return {"name": name}


def _sub_book_named(name: str) -> dict:
    sub = {"name": "part1", "pages": [{"type": "toc"}, "text/ch1.md"]}
    return _book([{"type": "book", "name": name, "book": sub}])


def _sub_book_content_named(name: str) -> dict:
    sub = {"name": name, "pages": [{"type": "toc"}, "text/ch1.md"]}
    return _book([{"type": "book", "book": sub}])


NAME_PLACES: dict[str, Callable[[str], dict]] = {
    "chapter": _chapter_named,
    "toc-page": _toc_named,
    "book": _book_named,
    "sub-book-page": _sub_book_named,
    "sub-book-content": _sub_book_content_named,
}


@pytest.mark.parametrize("place", NAME_PLACES)
@pytest.mark.parametrize("name", DANGEROUS_NAMES, ids=repr)
def test_dangerous_names_are_rejected(project: Project, place: str, name: str):
    project.manifest(book=NAME_PLACES[place](name))

    with pytest.raises(ValidationError):
        Manifest.load_from_file(project.manifest_path)


@pytest.mark.parametrize("place", NAME_PLACES)
@pytest.mark.parametrize("name", ["part-1", "Prolog", "ch_2", ".hidden", "..a", "a..", "v1.2"], ids=repr)
def test_harmless_names_are_accepted(project: Project, place: str, name: str):
    """Control test: the rule must not be stricter than needed."""
    project.manifest(book=NAME_PLACES[place](name))

    assert Manifest.load_from_file(project.manifest_path).title == "Test Book"


@pytest.mark.parametrize("name", ["contents", "my-toc", ".hidden", "..a"])
def test_page_name_is_the_file_name_and_stays_inside_the_book_folder(project: Project, name: str):
    project.manifest(book=_toc_named(name))

    epub = zipfile.ZipFile(project.build())

    assert f"OEBPS/content/{name}.xhtml" in epub.namelist()
    assert leaks(epub) == []


def test_dots_in_a_page_name_are_kept_in_the_file_name(project: Project):
    project.manifest(book=_toc_named("part.01"))

    assert "OEBPS/content/part.01.xhtml" in zipfile.ZipFile(project.build()).namelist()
