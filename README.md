<p align="center">
  <img src="md2epub/static/logo.svg" alt="md2epub logo" width="380">
</p>

<h1 align="center">md2epub</h1>

<p align="center">A command-line tool that builds valid EPUB publications from Markdown chapters, driven by a YAML/JSON manifest.</p>

## About

md2epub was built to solve a specific need: converting a set of Markdown-written chapters into a proper EPUB file for a personal writing project. Rather than hand-rolling EPUB's XML/OPF structure, it lets you describe a book's metadata and page structure in a manifest file, then generates a spec-compliant EPUB from your Markdown source — cover, title page, table of contents, and chapters included.

The manifest maps directly onto the EPUB OPF 2.0.1 specification (the code links to the relevant spec section next to most fields), so the generated metadata — title, language, publication dates, identifiers, and so on — is what e-readers actually expect, not an approximation of it.

## Features

- **Manifest-driven builds** — describe metadata and page order in YAML or JSON; md2epub generates the EPUB's OPF, NCX table of contents, and every content page.
- **Page types beyond plain chapters** — cover, title, table of contents, and custom pages rendered from your own Jinja template, alongside Markdown chapters.
- **Book collections** — a page can be a whole nested sub-book, either written inline or loaded from another manifest file with `include_file`, so several independently-buildable books can share one folder and be assembled into a collection.
- **Security-conscious by default** — Markdown extensions are limited to an allow-list (Markdown's own built-ins plus md2epub's) unless you explicitly pass `--trust-extensions`; rendered HTML is sanitized; Jinja templates run in a sandboxed, auto-escaping environment; every path from the manifest is resolved and checked to stay inside the project.
- **An OpenAPI-shaped manifest reference, generated from the code** — `md2epub schema` exports the manifest's own Pydantic models as an OpenAPI document plus a browsable Swagger UI page, so the reference can never drift from what the models actually accept.
- **`md2epub init`** scaffolds a starter project (manifest, folders, a placeholder chapter and stylesheet) so there's something to build right away.
- **`md2epub unpack`** extracts an existing EPUB back into loose files, for inspecting or reworking one you don't have the original project for.
- Every EPUB also gets a small, non-linear copyright/colophon page crediting md2epub itself — see [Status](#status) for the honest state of the project.

## Installation

Not yet published on PyPI (the planned distribution name is `markdown2epub` — the `md2epub` name itself is taken by an unrelated package). Install from source with [uv](https://docs.astral.sh/uv/):

```bash
git clone https://github.com/vojtech-krupicka/py-md2epub.git
cd py-md2epub
uv sync
```

or with plain `pip`:

```bash
pip install .
```

Requires Python 3.12+.

## Usage

See [`examples/`](examples/) for three complete, working manifests from minimal to a multi-book
collection — each builds on its own with no setup beyond `md2epub build`.

```bash
md2epub init -o my-book       # scaffold a starter project
md2epub build my-book/manifest.yaml my-book.epub
```

- `MANIFEST` — path to a manifest file (YAML or JSON), or a directory containing one (looks for `manifest.yml`/`.yaml`/`.json`). If omitted, the current directory is used.
- `EPUB_FILE` — output path. If it's an *existing* directory, the output filename is derived from the manifest's name and placed inside it. If omitted, it's inferred the same way next to the manifest. Otherwise, it's used as the literal output file path.

```bash
mkdir -p output
md2epub build --overwrite ./my-book ./output/
```

Other commands:

```bash
md2epub unpack -i book.epub -o extracted/     # pull an EPUB's files back out
md2epub schema -o manifest-reference/         # generate openapi.yaml + a Swagger UI page for the manifest format
```

Every command accepts `-v`/`-q` for more or less logging, and `-h`/`--help` for its full option list; `md2epub build --help` in particular documents input/output path resolution in detail.

## Manifest reference

The manifest describes a book's metadata, build configuration, and page structure. Fields are validated with Pydantic; the authoritative, always-up-to-date reference is generated straight from those models:

```bash
md2epub schema -o manifest-reference/
```

This writes `openapi.yaml` (an OpenAPI document, `components.schemas` only — there are no real API paths, just the manifest's shapes) and `swagger-ui.html`, a browsable page listing every field, its type, default, and description. The overview below is a quick orientation, not a substitute for it.

### Top-level shape

```yaml
name: my-book              # technical name, used inside the EPUB's own folder structure; derived from
                            # the manifest's folder if omitted
metadata:
  title: My Book           # required
  author: Jane Doe         # shorthand for {name: Jane Doe}; full form also accepts role/file_as
  language: en
  # ...subtitle, identifiers, subjects, description, publisher, contributors, rights, calibre metadata;
  # book_id and the created/published/modified dates are all derived automatically if left unset

config:
  markdown:
    additional_extensions: [tables]   # only Markdown's own extensions and md2epub's are allowed by
                                       # default; anything else needs --trust-extensions on build

stylesheets: [styles/book.css]
files: [images]             # extra files/folders to bundle even if no page references them directly

pages:
  - type: cover
    cover_image: images/cover.jpg
  - type: title
  - type: toc
  - chapters/01-introduction.md      # a plain string is shorthand for {type: chapter, source: ...}
  - type: chapter
    source: chapters/02-getting-started.md
```

### Page types

| Type | Purpose | Key fields |
|---|---|---|
| `cover` | Cover image page | `cover_image` |
| `title` | Title page | `images`, `render_title`, `render_metadata`, `additional_content` |
| `toc` | Table of contents | `title`, `render_links`, `render_depth` |
| `chapter` | A Markdown chapter | `source` (required) |
| `custom` | Rendered from your own Jinja template | `template` (required), `sources`, `values` |
| `book` | A nested sub-book, inline or via `include_file` | `book`, `include_file` |

Every page also accepts `name`, `toc_title`, `stylesheets`/`stylesheets_overrides`, `add_to_toc`, and `custom_template`. Several shorthands expand into more than one page — e.g. `{type: cover_title_toc}` is `cover` + `title` + `toc` in one entry.

A `book`-type page's own `book:` is a full nested manifest (its own `metadata`, `pages`, etc.) — either written inline, or loaded from another file entirely via `include_file: other-manifest.yaml`, which lets several independently-buildable manifests live in the same folder and be assembled into one collection.

## Security

Because a manifest and its Markdown are treated as input from a project you may not fully trust (or may be sharing/collaborating on), md2epub applies several defenses by default rather than as opt-ins:

- Markdown extensions are limited to Markdown's own built-ins and `md2epub.extensions.*` unless `--trust-extensions` is passed — an extension is a Python module that gets imported and executed, so this isn't optional by default.
- Rendered chapter HTML is sanitized (via [nh3](https://nh3.readthedocs.io/)) before being embedded.
- Every Jinja template — including any custom one a manifest points at — renders in a sandboxed, auto-escaping environment.
- Every path read from the manifest (chapter sources, images, stylesheets, `include_file`, custom templates) is resolved and checked to stay inside the project; none can escape via `..` or an absolute path.

## Roadmap

Ideas for after the first release, roughly in order of how likely they are to land first:

- **Round-trip `unpack`/`build`** — support HTML/XHTML/TXT chapter sources directly (not only Markdown), so an unpacked EPUB's XHTML chapters can be rebuilt without a lossy conversion to Markdown, and `unpack` can reconstruct a real `manifest.yaml` from an EPUB's OPF/spine instead of just extracting files.
- **Interactive `init`** — build the manifest and starter chapters from CLI prompts instead of a fixed placeholder scaffold.
- **Built-in themes** — a `theme` field offering a small set of packaged stylesheets (`default`, `modern`, `sci-fi`, `historical`, ...) that a book or page can opt into, stacking with any custom stylesheets you still provide.
- **Auto-numbered sequences** — a book-level declaration of named counters, marked inline in Markdown (e.g. `!SEQ[figures]`) and replaced with an increasing, formatted number at build time, so reordering chapters doesn't mean renumbering figures by hand.

## Status

**Early / experimental.** Built for a specific personal writing project — functional, with a real test suite and a fair amount of hardening against untrusted manifests, but not yet battle-tested across a wide range of real-world books. No versioned release yet — see [CHANGELOG.md](CHANGELOG.md).

## Development

This project uses [uv](https://docs.astral.sh/uv/):

```bash
uv sync --extra dev
uv run pytest
```

A [Dockerfile](Dockerfile) and [devcontainer](.devcontainer/devcontainer.json) are also provided for a ready-to-go development environment.

## License

MIT — see [LICENSE](LICENSE).
