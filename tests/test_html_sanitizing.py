"""
Raw HTML inside Markdown.

Python-Markdown passes raw HTML through untouched, so a chapter can carry `<script>`, `onerror=`, `javascript:`
links or remote images into the EPUB. The output is EPUB 2 (XHTML 1.1): there is no scripting, no inline event
handlers and no remote resources, and a reader that supports them anyway should not get them from us.

The rule these tests describe: harmless markup survives, everything active is removed.
"""

from __future__ import annotations

import re
from urllib.parse import urlsplit

import pytest
from lxml import etree

from md2epub.core.content_creator import ContentCreator, ContentType
from md2epub.models.public.manifest import Manifest

BANNED_TAGS = {"script", "iframe", "object", "embed", "applet", "style", "link", "meta", "base", "form", "input", "svg"}
URL_ATTRIBUTES = {"href", "src", "data", "action", "formaction", "poster", "background"}
ACTIVE_SCHEMES = re.compile(r"\s*(javascript|vbscript|data):", re.IGNORECASE)


@pytest.fixture
def creator() -> ContentCreator:
    return ContentCreator(Manifest.load_from_string("title: T\nbook: {name: content, pages: [x.md]}"))


def convert(creator: ContentCreator, markdown: str) -> str:
    return creator.create(markdown, ContentType.Markdown)


def tree(xhtml: str) -> etree._Element:
    return etree.fromstring(f"<root>{xhtml}</root>")


def problems(xhtml: str) -> list[str]:
    """Everything active in the (well-formed) XHTML: banned elements, event handlers, script URLs, remote images."""
    found: list[str] = []
    for el in tree(xhtml).iter():
        if not isinstance(el.tag, str):
            continue
        tag = el.tag.lower()
        if tag in BANNED_TAGS:
            found.append(f"<{tag}> element")
        for name, value in el.attrib.items():
            name = name.lower()
            if name.startswith("on"):
                found.append(f"<{tag} {name}=...> event handler")
            if name in URL_ATTRIBUTES and ACTIVE_SCHEMES.match(value):
                found.append(f"<{tag} {name}={value!r}> script URL")
            if tag == "img" and name == "src" and (urlsplit(value).scheme or urlsplit(value).netloc):
                found.append(f"<img src={value!r}> remote image")
    return found


# region Active content is removed

ACTIVE_CONTENT = {
    "script-block": "<script>alert(1)</script>",
    "script-inline": "text <script>alert(1)</script> more text",
    "img-onerror": '<img src="x" onerror="alert(1)">',
    "img-onerror-uppercase": "<IMG SRC=x ONERROR=alert(1)>",
    "div-onclick": '<div onclick="alert(1)">click me</div>',
    "javascript-link-html": '<a href="javascript:alert(1)">click</a>',
    "javascript-link-markdown": "[click](javascript:alert(1))",
    "javascript-link-obfuscated": '<a href="  JaVaScRiPt:alert(1)">click</a>',
    "iframe": '<iframe src="http://evil.example/"></iframe>',
    "object": '<object data="http://evil.example/x.swf"></object>',
    "embed": '<embed src="http://evil.example/x.swf">',
    "style-import": "<style>@import url(http://evil.example/a.css);</style>",
    "svg-onload": "<svg onload=alert(1)></svg>",
    "form": '<form action="http://evil.example/"><input name="x"></form>',
    "remote-image-html": '<img src="http://tracker.example/p.gif" alt="">',
    "remote-image-markdown": "![tracker](https://tracker.example/p.gif)",
    "protocol-relative-image": '<img src="//tracker.example/p.gif" alt="">',
}


@pytest.mark.parametrize("markdown", ACTIVE_CONTENT.values(), ids=ACTIVE_CONTENT.keys())
def test_active_content_is_removed(creator: ContentCreator, markdown: str):
    assert problems(convert(creator, markdown)) == []


def test_a_document_of_nothing_but_a_script_does_not_break_the_build(creator: ContentCreator):
    """Sanitizing can leave nothing at all, that must give an empty chapter and not an lxml error."""
    assert problems(convert(creator, "<script>alert(1)</script>")) == []


# region Harmless content survives

SURVIVES = {
    "emphasis": ("*em* and **strong**", "//em", "//strong"),
    "raw-inline-tags": ("<em>raw</em> <span class='note'>span</span>", "//em", "//span[@class='note']"),
    "line-break": ("one<br />two", "//br"),
    "relative-image": ('<img src="../images/pic.png" alt="pic" />', "//img[@src='../images/pic.png']"),
    "relative-image-markdown": ("![pic](../images/pic.png)", "//img[@src='../images/pic.png']"),
    "external-link": ("[site](https://example.com/a?b=1&c=2)", "//a[@href='https://example.com/a?b=1&c=2']"),
    "mail-link": ("[me](mailto:me@example.com)", "//a[@href='mailto:me@example.com']"),
    "anchor-link": ("[top](#top)", "//a[@href='#top']"),
    "table": ("| a | b |\n|---|---|\n| 1 | 2 |\n", "//table//th", "//table//td"),
    "fenced-code": ("```\nx < y\n```\n", "//pre/code"),
    "attr-list": ("A paragraph.\n{: #intro .lead }", "//p[@id='intro'][@class='lead']"),
    "block-div-with-class": ('<div class="centered">\n\ntext\n\n</div>', "//div[@class='centered']"),
    "heading": ("# Title\n\n## Sub", "//h1", "//h2"),
    "unordered-list": ("- a\n- b", "//ul/li"),
    "ordered-list": ("1. x\n2. y", "//ol/li"),
    "blockquote": ("> quoted", "//blockquote"),
}


@pytest.mark.parametrize(("markdown", "expected"), [(v[0], v[1:]) for v in SURVIVES.values()], ids=SURVIVES.keys())
def test_harmless_markup_survives(creator: ContentCreator, markdown: str, expected: tuple[str, ...]):
    root = tree(convert(creator, markdown))

    for xpath in expected:
        assert root.xpath(xpath), f"{xpath} is missing"


def test_text_and_typography_survive(creator: ContentCreator):
    text = "".join(tree(convert(creator, 'Salt & pepper, 5 < 6, "quoted", k lesu.')).itertext())

    assert "Salt & pepper, 5 < 6" in text
    assert (
        "\N{DOUBLE LOW-9 QUOTATION MARK}quoted\N{LEFT DOUBLE QUOTATION MARK}" in text
    )  # Czech smart quotes from `smarty`
    assert "k\N{NO-BREAK SPACE}lesu" in text  # from the default `vlna` extension
