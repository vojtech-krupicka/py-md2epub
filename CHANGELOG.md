# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0] - 2026-10-01

First release. Everything below is the initial feature set, not a diff from a prior version.

### Added

- `md2epub build MANIFEST EPUB_FILE` — build a spec-compliant EPUB from a YAML/JSON manifest and
  Markdown chapters: cover, title, table of contents and chapter pages, with a generated OPF and NCX.
- `md2epub init` — scaffold a starter project (manifest, folders, a placeholder chapter and
  stylesheet) so there's something to build right away.
- `md2epub unpack` — extract an existing EPUB back into loose files, for inspecting or reworking one
  you don't have the original project for. Currently a raw extraction; reconstructing a full
  `manifest.yaml` from the OPF/spine is planned (see the roadmap in the README).
- `md2epub schema` — export the manifest format's own Pydantic models as an OpenAPI document plus a
  browsable Swagger UI page, so the reference can never drift from what the models actually accept.
- Custom page type, rendered from your own Jinja template with named source files and arbitrary
  values passed through.
- Book collections: a page can be a whole nested sub-book, written inline or loaded from another
  manifest file via `include_file`, so several independently-buildable books can share one folder
  and be assembled into a collection.
- An automatic, non-linear copyright/colophon page on every build, crediting the project.
- A project logo and favicon, embedded as self-contained inline SVG (every letter of the wordmark is
  a pre-outlined path from the real font files, so no EPUB reader can render it with a substituted
  font) on both the copyright page and the `schema` command's Swagger UI page.

### Security

- Markdown extensions are limited to an allow-list (Markdown's own built-ins plus `md2epub`'s) unless
  `--trust-extensions` is explicitly passed — a manifest is untrusted input, and an extension is a
  Python module that gets imported and executed.
- Rendered chapter HTML is sanitized before being embedded.
- Every Jinja template, including any custom one a manifest points at, renders in a sandboxed,
  auto-escaping environment.
- Every path read from the manifest (chapter sources, images, stylesheets, `include_file`, custom
  templates) is resolved and checked to stay inside the project; none can escape via `..` or an
  absolute path.

