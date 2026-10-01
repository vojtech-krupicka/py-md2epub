# Roadmap

Ideas for after the first release, roughly in order of how likely they are to land first:

- **Round-trip `unpack`/`build`** — support HTML/XHTML/TXT chapter sources directly (not only
  Markdown), so an unpacked EPUB's XHTML chapters can be rebuilt without a lossy conversion to
  Markdown, and `unpack` can reconstruct a real `manifest.yaml` from an EPUB's OPF/spine instead of
  just extracting files.
- **Interactive `init`** — build the manifest and starter chapters from CLI prompts instead of a
  fixed placeholder scaffold.
- **Built-in themes** — a `theme` field offering a small set of packaged stylesheets (`default`,
  `modern`, `sci-fi`, `historical`, ...) that a book or page can opt into, stacking with any custom
  stylesheets you still provide.
- **Auto-numbered sequences** — a book-level declaration of named counters, marked inline in Markdown
  (e.g. `!SEQ[figures]`) and replaced with an increasing, formatted number at build time, so
  reordering chapters doesn't mean renumbering figures by hand.

None of these are scheduled — they're the current best guesses for where the project goes after
0.1.0.
