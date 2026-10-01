# Examples

Three manifests, in increasing order of what they show off. Each builds on its own:

```bash
md2epub build examples/01-minimal/manifest.yaml minimal.epub
md2epub build examples/02-full-featured/manifest.yaml full-featured.epub
md2epub build examples/03-collection/manifest.yaml collection.epub
```

- **[`01-minimal/`](01-minimal/)** - the smallest manifest md2epub accepts: a title, an author, a
  cover/title/toc shorthand, and two plain chapters.
- **[`02-full-featured/`](02-full-featured/)** - more of the metadata fields (subtitle, additional
  authors, contributors, rights, a Calibre series), a custom stylesheet, a title page image, a
  per-chapter table-of-contents override, a Markdown extension enabled via `config.markdown`, and a
  `custom` page rendered from its own Jinja template.
- **[`03-collection/`](03-collection/)** - a book made of two otherwise-independent books
  (`part-1-foundations/` and `part-2-advanced/`), each with its own `manifest.yaml` that builds fine
  on its own, assembled into one EPUB by a top-level manifest using `include_file`.
