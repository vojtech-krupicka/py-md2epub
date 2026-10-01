# Manifest reference

The manifest describes a book's metadata, build configuration, and page structure. Fields are
validated with Pydantic; the authoritative, always-up-to-date reference is generated straight from
those models:

```bash
md2epub schema -o docs/manifest-reference/
```

This writes `openapi.yaml` (an OpenAPI document, `components.schemas` only — there are no real API
paths, just the manifest's shapes) and `swagger-ui.html`, a browsable page listing every field, its
type, default, and description, embedded below. The overview on this page is a quick orientation,
not a substitute for it.

<iframe src="swagger-ui.html" title="md2epub manifest schema" style="width: 100%; height: 80vh; border: 1px solid var(--md-default-fg-color--lightest);"></iframe>

The raw document is also available at [openapi.yaml](manifest-reference/openapi.yaml).

## Top-level shape

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

## Page types

| Type | Purpose | Key fields |
|---|---|---|
| `cover` | Cover image page | `cover_image` |
| `title` | Title page | `images`, `render_title`, `render_metadata`, `additional_content` |
| `toc` | Table of contents | `title`, `render_links`, `render_depth` |
| `chapter` | A Markdown chapter | `source` (required) |
| `custom` | Rendered from your own Jinja template | `template` (required), `sources`, `values` |
| `book` | A nested sub-book, inline or via `include_file` | `book`, `include_file` |

Every page also accepts `name`, `toc_title`, `stylesheets`/`stylesheets_overrides`, `add_to_toc`, and
`custom_template`. Several shorthands expand into more than one page — e.g. `{type: cover_title_toc}`
is `cover` + `title` + `toc` in one entry.

A `book`-type page's own `book:` is a full nested manifest (its own `metadata`, `pages`, etc.) —
either written inline, or loaded from another file entirely via `include_file: other-manifest.yaml`,
which lets several independently-buildable manifests live in the same folder and be assembled into
one collection. See the [`03-collection`](https://github.com/vojtech-krupicka/py-md2epub/tree/main/examples/03-collection)
example.
