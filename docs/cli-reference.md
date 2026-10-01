# CLI reference

Every command accepts `-v`/`-q` for more or less logging, `--log-cfg-path` for a custom logging
config, and `-h`/`--help` for its full option list. The top-level `-V`/`--version` flag prints the
installed version.

## `md2epub build`

```bash
md2epub build [OPTIONS] [MANIFEST] [EPUB_FILE]
```

Build an EPUB from an input `MANIFEST` into an output `EPUB_FILE`.

`MANIFEST` can be a YAML (`.yml`, `.yaml`) or JSON (`.json`) file, or a directory:

- a valid file is read as-is, and its parent folder becomes the working directory;
- a valid directory is searched for `manifest.yml`, `manifest.yaml`, or `manifest.json` in that
  order, and the directory itself becomes the working directory;
- if omitted, the current directory is used, with the same search as above.

`EPUB_FILE` is the output:

- an *existing* directory gets a filename derived from the manifest's name, placed inside it;
- if omitted, the same derivation is used, placed next to the manifest;
- anything else is used as the literal output file path.

The `.epub` extension is added automatically if missing (configurable via
`config.md2epub.epub_suffix` in the manifest).

| Option | Description |
|---|---|
| `--overwrite` | Overwrite `EPUB_FILE` if it already exists; otherwise build fails on a conflict. |
| `--trust-extensions` | Allow any Markdown extension named in the manifest, not only the built-in and md2epub ones. An extension is a Python module that gets imported and executed, so this is opt-in on purpose — see [Security](security.md). |
| `--zip` | Write a plain `.zip` instead of a valid `.epub` (handy for inspecting the generated package). |

## `md2epub init`

```bash
md2epub init [OPTIONS]
```

Scaffold a starter project: a manifest plus the folder structure it expects (chapters, images,
styles), so `md2epub build` has something to build right away.

| Option | Description |
|---|---|
| `-o`, `--output-dir` | Directory to initialize into (must be empty, created if missing). Defaults to the current directory. |

## `md2epub unpack`

```bash
md2epub unpack -i INPUT_EPUB [OPTIONS]
```

Unpack an existing EPUB back into loose files, for inspecting or reworking one you don't have the
original project for.

Currently does only raw extraction — every file in the EPUB is written out as-is. Reconstructing a
`manifest.yaml` from the OPF/spine is planned; see [Roadmap](roadmap.md).

| Option | Description |
|---|---|
| `-i`, `--input-epub` | Path to the input EPUB file. **Required.** |
| `-o`, `--output-dir` | Directory to unpack into (must be empty, created if missing). Defaults to the current directory. |

## `md2epub schema`

```bash
md2epub schema [OPTIONS]
```

Generate the manifest schema as an OpenAPI document plus a browsable Swagger UI page — see
[Manifest reference](manifest-reference.md).

| Option | Description |
|---|---|
| `-o`, `--output-dir` | Directory to write `openapi.yaml` and `swagger-ui.html` into (created if missing). Defaults to the current directory. |
