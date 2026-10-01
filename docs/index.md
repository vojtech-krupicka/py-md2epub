# md2epub

<p align="center">
  <img src="assets/logo.svg" alt="md2epub logo" width="380">
</p>

A command-line tool that builds valid EPUB publications from Markdown chapters, driven by a
YAML/JSON manifest.

## About

md2epub was built to solve a specific need: converting a set of Markdown-written chapters into a
proper EPUB file for a personal writing project. Rather than hand-rolling EPUB's XML/OPF structure,
it lets you describe a book's metadata and page structure in a manifest file, then generates a
spec-compliant EPUB from your Markdown source — cover, title page, table of contents, and chapters
included.

The manifest maps directly onto the EPUB OPF 2.0.1 specification (the code links to the relevant
spec section next to most fields), so the generated metadata — title, language, publication dates,
identifiers, and so on — is what e-readers actually expect, not an approximation of it.

## Features

- **Manifest-driven builds** — describe metadata and page order in YAML or JSON; md2epub generates
  the EPUB's OPF, NCX table of contents, and every content page.
- **Page types beyond plain chapters** — cover, title, table of contents, and custom pages rendered
  from your own Jinja template, alongside Markdown chapters.
- **Book collections** — a page can be a whole nested sub-book, either written inline or loaded from
  another manifest file with `include_file`, so several independently-buildable books can share one
  folder and be assembled into a collection.
- **Security-conscious by default** — Markdown extensions are limited to an allow-list, rendered HTML
  is sanitized, Jinja templates run sandboxed, and every manifest path is checked to stay inside the
  project. See [Security](security.md) for the full picture.
- **An OpenAPI-shaped manifest reference, generated from the code** — `md2epub schema` exports the
  manifest's own Pydantic models as an OpenAPI document plus a browsable Swagger UI page, so the
  reference can never drift from what the models actually accept. See
  [Manifest reference](manifest-reference.md).
- **`md2epub init`** scaffolds a starter project so there's something to build right away.
- **`md2epub unpack`** extracts an existing EPUB back into loose files.
- Every EPUB also gets a small, non-linear copyright/colophon page crediting md2epub itself.

## Status

**Early / experimental.** Built for a specific personal writing project — functional, with a real
test suite and a fair amount of hardening against untrusted manifests, but not yet battle-tested
across a wide range of real-world books. See the
[CHANGELOG](https://github.com/vojtech-krupicka/py-md2epub/blob/main/CHANGELOG.md) for release
history.

Start with [Getting started](getting-started.md).
