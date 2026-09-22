from __future__ import annotations

import pkgutil

import markdown.extensions

import md2epub.extensions


def _builtin_markdown_extensions() -> frozenset[str]:
    """Extension names that ship inside the `Markdown` package itself, e.g. 'toc', 'tables', 'smarty'."""
    return frozenset(m.name for m in pkgutil.iter_modules(markdown.extensions.__path__))


def _md2epub_extensions() -> frozenset[str]:
    """Extension names that ship inside `md2epub.extensions`, e.g. 'md2epub.extensions.vlna'."""
    return frozenset(f"md2epub.extensions.{m.name}" for m in pkgutil.iter_modules(md2epub.extensions.__path__))


def is_trusted_extension(name: str, *, trust_all: bool = False) -> bool:
    """
    A Markdown extension is trusted if it ships with `Markdown` or with `md2epub` - both come from the
    installed package, not from the project being built. Anything else is a dotted path to a Python module,
    which `Markdown` will import and run: a manifest is untrusted input and must not be able to name one
    unless the person running the build explicitly opted in (`trust_all`, e.g. `--trust-extensions`).
    """
    if trust_all:
        return True

    return name in _builtin_markdown_extensions() or name in _md2epub_extensions()


def assert_trusted_extensions(names: list[str], *, trust_all: bool = False) -> None:
    """Raise if any of `names` is not trusted, see `is_trusted_extension`."""
    untrusted = [name for name in names if not is_trusted_extension(name, trust_all=trust_all)]
    if untrusted:
        raise PermissionError(
            f"Refusing to load untrusted Markdown extension(s): {', '.join(untrusted)}. Only Markdown's "
            "built-in extensions and 'md2epub.extensions.*' are allowed by default; pass --trust-extensions "
            "if you trust this project's own extensions."
        )
