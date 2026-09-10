# md2epub

A command-line tool that builds valid EPUB publications from Markdown chapters, driven by a YAML/JSON manifest file.

## About

md2epub was built to solve a specific need: converting a set of Markdown-written chapters into a proper EPUB file for a personal writing project. Rather than hand-rolling EPUB's XML/OPF structure, it lets you describe the book's metadata and chapter order in a simple manifest file, then generates a spec-compliant EPUB from your Markdown source.

The manifest format follows the EPUB OPF 2.0.1 specification directly (see inline references to the spec in the code), so the generated metadata — title, language, publication dates, and so on — maps cleanly to what e-readers expect.

## Features

- Builds an EPUB from Markdown chapter files plus a YAML or JSON manifest
- Manifest schema validated with Pydantic, based on the EPUB OPF 2.0.1 spec
- Flexible input/output resolution — point it at a manifest file, a directory containing one, or just run it in a directory and let it find `md2epub.yml`/`manifest.yml` (or `.yaml`/`.json`) automatically
- `--overwrite` flag for regenerating output during iteration
- `--verbose` / `--quiet` logging control

## Tech Stack

Python 3.9+, [Click](https://click.palletsprojects.com/) (CLI), [Pydantic](https://docs.pydantic.dev/) (manifest validation), [Jinja2](https://jinja.palletsprojects.com/) (templating), [PyYAML](https://pyyaml.org/), [Markdown](https://python-markdown.github.io/).

## Installation

Not yet published on PyPI. Install from source:

```bash
git clone https://github.com/vojtech-krupicka/md2epub.git
cd md2epub
pip install .
```

## Usage

```bash
md2epub build MANIFEST EPUB_FILE
```

- `MANIFEST` — path to a manifest file (YAML or JSON), or a directory containing one (looks for `md2epub.yml`/`.yaml`/`.json` or `manifest.yml`/`.yaml`/`.json`). If omitted, the current directory is used.
- `EPUB_FILE` — output path. If a directory is given, the output filename is derived from the manifest name. If omitted, it's inferred automatically.

```bash
md2epub build --overwrite ./my-book ./output/
```

Run `md2epub build --help` for the full option list.

## Manifest Reference

The manifest describes the book's metadata and its page structure. Fields are validated with Pydantic; most are optional and follow the [EPUB OPF 2.0.1 spec](https://idpf.org/epub/20/spec/OPF_2.0.1_draft.htm).

### Top-level fields

| Field | Type | Default | Notes |
|---|---|---|---|
| `title` | str | — | **Required.** Book title. |
| `subtitle` | str | `""` | |
| `author` | str or object | — | Shorthand: just a name string. Full form: `{name, role, file_as}`. |
| `additional_authors` | list | `[]` | Additional co-authors, same shape as `author`. |
| `language` | str | `"en"` | |
| `created` / `published` / `modified` | str/int | today's date | Auto-filled if omitted (`YYYY` for `created`, `YYYY-MM-DD` for the others). |
| `book_id` | object | random UUID | `{scheme, value, id}` — unique book identifier. |
| `identifiers` | list | `[]` | Additional identifiers (ISBN, etc.): `{scheme, value}`. |
| `subjects` | list[str] | `[]` | Keywords/tags. |
| `description` | str | `""` | |
| `publisher` | str | `""` | |
| `contributors` | list | `[]` | Secondary contributors: `{role, name, file_as}`. |
| `rights` | list[str] | `[]` | |
| `calibre` | object | — | Calibre metadata: `{title_sort, series, series_index, author_link_map}`. |
| `book` | object | — | **Required.** Contains `pages` — see below. |

### Pages (`book.pages`)

Each entry in `book.pages` can be:
- a **plain string** — shorthand for a chapter, treated as `{type: chapter, source: <string>}`
- a **dict** with a `type` key: `cover`, `title`, `toc`, `chapter`, `custom`, or `book` (nested book part). Omitting `type` defaults to `chapter`.

| Type | Key fields |
|---|---|
| `cover` | `cover_image` (path, default `images/cover.jpg`) |
| `title` | `images`, `render_title`, `render_metadata`, `additional_content` |
| `toc` | `title`, `render_links`, `render_depth` |
| `chapter` | `source` (required — path to a Markdown file), `sequence` |
| `custom` | `template` (required), `sources` (dict), `values` (dict) |
| `book` | nested `book` object (for multi-part books) |

All page types also accept: `name`, `title`, `subtitle`, `supertitle`, `stylesheets`, `add_to_toc`, `custom_template`.

### Example manifest (YAML)

```yaml
title: My Book
subtitle: A Collection of Notes
author: Vojtěch Krupička
language: en
description: A short example manifest for md2epub.
subjects:
  - notes
  - example

book:
  pages:
    - type: cover
      cover_image: images/cover.jpg
    - type: title
    - type: toc
    - type: chapter
      source: chapters/01-introduction.md
    - type: chapter
      source: chapters/02-getting-started.md
    - chapters/03-conclusion.md   # shorthand: plain string = chapter
```

## Status

**Early / experimental.** Built for a specific personal writing project — functional, but not yet battle-tested across a wide range of manifests or edge cases. No versioned releases yet (see `CHANGELOG.md`).

## License

MIT — see [LICENSE](LICENSE).
