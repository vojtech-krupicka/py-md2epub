from __future__ import annotations

from urllib.parse import urlsplit

import nh3

# Plain XHTML 1.1 markup which Markdown and its default extensions produce, plus what people write by hand.
ALLOWED_TAGS = set(
    "a abbr b blockquote br caption cite code col colgroup dd del div dl dt em h1 h2 h3 h4 h5 h6 hr i img ins kbd li "  # noqa: SIM905
    "ol p pre q s samp small span strong sub sup table tbody td tfoot th thead tr u ul var".split()
)

# No `style` and no `on*` handlers: styling belongs into stylesheets, there is no scripting in EPUB 2.
ALLOWED_ATTRIBUTES = {
    "*": {"class", "id", "title", "lang", "dir"},
    "a": {"href"},
    "img": {"src", "alt", "width", "height"},
    "td": {"colspan", "rowspan", "align"},
    "th": {"colspan", "rowspan", "align"},
    "col": {"span"},
    "colgroup": {"span"},
    "ol": {"start"},
}

# Links may leave the book, but never run code (`javascript:`, `vbscript:`, `data:`).
ALLOWED_URL_SCHEMES = {"http", "https", "mailto"}


def _attribute_filter(tag: str, attribute: str, value: str) -> str | None:
    # EPUB 2 keeps all resources inside the book: a remote image is dropped (and it would be a tracking pixel).
    if tag == "img" and attribute == "src":
        parts = urlsplit(value.strip())
        if parts.scheme or parts.netloc:
            return None
    return value


def sanitize_html(html: str) -> str:
    """
    Remove everything active from HTML which comes from a Markdown source: scripts, styles, frames, forms,
    event handlers, script URLs and remote images. Harmless markup, text and entities are kept.
    """

    return nh3.clean(
        html,
        tags=ALLOWED_TAGS,
        clean_content_tags={"script", "style"},
        attributes=ALLOWED_ATTRIBUTES,
        url_schemes=ALLOWED_URL_SCHEMES,
        attribute_filter=_attribute_filter,
        link_rel=None,
    )
