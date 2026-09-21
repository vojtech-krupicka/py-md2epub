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

from md2epub.commands import build
from tests.conftest import Project
from tests.helpers import build_or_refuse, leaks

KNOWN = pytest.mark.xfail(strict=True)

# region Paths from the manifest must stay inside the project


def _book(pages=(), **extra) -> dict:
    return {"pages": [{"type": "toc"}, *pages], **extra}


# id -> (builds the `book` part of the manifest from a dict of references to the outside files, known bug?)
ESCAPES: dict[str, tuple[Callable[[dict], dict], bool]] = {
    "chapter-relative": (lambda r: _book([{"type": "chapter", "source": r["md_rel"]}]), True),
    "chapter-absolute": (lambda r: _book([{"type": "chapter", "source": r["md_abs"]}]), True),
    "cover-relative": (lambda r: _book([{"type": "cover", "cover_image": r["png_rel"]}]), True),
    "cover-absolute": (lambda r: _book([{"type": "cover", "cover_image": r["png_abs"]}]), False),
    "stylesheet-relative": (lambda r: _book(["text/ch1.md"], stylesheets=[r["css_rel"]]), True),
    "stylesheet-absolute": (lambda r: _book(["text/ch1.md"], stylesheets=[r["css_abs"]]), False),
    "files-parent-directory": (lambda r: _book(["text/ch1.md"], files=[".."]), True),
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
