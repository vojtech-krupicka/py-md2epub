# Getting started

## Installation

Install from [PyPI](https://pypi.org/project/markdown2epub/) (the distribution is named
`markdown2epub` — the `md2epub` name itself is taken by an unrelated package — but the installed
command is still `md2epub`):

```bash
pip install markdown2epub
```

or with [uv](https://docs.astral.sh/uv/):

```bash
uv tool install markdown2epub
```

To install from source instead:

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

## Your first build

```bash
md2epub init -o my-book       # scaffold a starter project
md2epub build my-book/manifest.yaml my-book.epub
```

- `MANIFEST` — path to a manifest file (YAML or JSON), or a directory containing one (looks for
  `manifest.yml`/`.yaml`/`.json`). If omitted, the current directory is used.
- `EPUB_FILE` — output path. If it's an *existing* directory, the output filename is derived from
  the manifest's name and placed inside it. If omitted, it's inferred the same way next to the
  manifest. Otherwise, it's used as the literal output file path.

```bash
mkdir -p output
md2epub build --overwrite ./my-book ./output/
```

See [Examples](examples.md) for three complete, working manifests from minimal to a multi-book
collection, and [CLI reference](cli-reference.md) for every command and option.

## Next steps

- [Manifest reference](manifest-reference.md) — every field the manifest accepts.
- [Security](security.md) — what md2epub treats as untrusted input, and why.
