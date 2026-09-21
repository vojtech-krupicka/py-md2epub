"""Small helpers shared by the test modules."""

from __future__ import annotations

import base64
import zipfile
from typing import Any

from lxml import etree

# A valid 1x1 PNG, so that cover images used in tests are real images.
PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
)

# Text placed into files that live OUTSIDE of a test project. It must never end up inside an EPUB.
SECRET = "TOP-SECRET-MARKER"

# XML namespaces used inside an EPUB 2 package.
NS = {
    "opf": "http://www.idpf.org/2007/opf",
    "dc": "http://purl.org/dc/elements/1.1/",
    "x": "http://www.w3.org/1999/xhtml",
    "ncx": "http://www.daisy.org/z3986/2005/ncx/",
}


def xml_errors(epub: zipfile.ZipFile) -> dict[str, str]:
    """Return `{entry name: parser error}` for every XML part of the EPUB that is not well-formed."""
    errors: dict[str, str] = {}
    for name in epub.namelist():
        if name.endswith((".xhtml", ".opf", ".ncx", ".xml")):
            try:
                etree.fromstring(epub.read(name))
            except etree.XMLSyntaxError as e:
                errors[name] = str(e)
    return errors


def xml(epub: zipfile.ZipFile, name: str) -> Any:
    """Parse one XML part of the EPUB."""
    return etree.fromstring(epub.read(name))


def leaks(epub: zipfile.ZipFile, marker: str = SECRET) -> list[str]:
    """
    Return everything that is wrong with the EPUB from a security point of view: entry names that
    could escape the extraction folder (`..`, absolute) and entries which contain `marker`.
    """
    problems: list[str] = []
    for info in epub.infolist():
        if ".." in info.filename.split("/") or info.filename.startswith("/"):
            problems.append(f"unsafe entry name: {info.filename}")
        if marker.encode() in epub.read(info):
            problems.append(f"'{marker}' found in: {info.filename}")
    return problems


def build_or_refuse(project: Any, **kwargs: Any) -> zipfile.ZipFile | None:
    """
    Build the project. Refusing to build is a perfectly valid (and safe) reaction to a hostile
    manifest, so an exception is reported as `None` instead of failing the test.
    """
    try:
        return zipfile.ZipFile(project.build(**kwargs))
    except Exception:
        return None
