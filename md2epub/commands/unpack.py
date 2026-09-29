import zipfile
from pathlib import Path

EPUB_SUFFIX = ".epub"


def run(input_epub: Path, output_dir: Path) -> bool:
    """
    Run the unpack command.

    Currently a raw, best-effort extraction: every file the EPUB contains (mimetype, OPF, NCX, and
    every content/asset file) is written out as-is. Reconstructing a `manifest.yaml` from the OPF/NCX,
    and converting XHTML chapters back to Markdown, is not implemented yet.
    """

    # Resolve input path
    epub_path = resolve_input(input_epub)

    # Resolve output folder, create it if not exists and check if it is empty
    output_path = resolve_output(output_dir)

    # `ZipFile.extractall()` is safe against zip-slip on its own: it strips any leading `/`, drive
    # letter and `..`/`.` path components from each entry name before writing, so a hostile EPUB
    # cannot write outside `output_path` (unlike `Epub.add()`'s own `safe_entry_name()`, this
    # sanitizing happens inside the stdlib, not this codebase - nothing else to check here).
    with zipfile.ZipFile(epub_path, "r") as zip_ref:
        zip_ref.extractall(output_path)

    return True


def resolve_input(path: Path) -> Path:
    """Return the resolved path to the epub file."""

    # `resolve()` matters: `Path(".").name` is "" and `Path.cwd()` may be a symlink
    path = (path if path is not None else Path.cwd()).resolve()

    # Path must exist
    if not path.exists():
        raise FileNotFoundError(f"Path '{path}' does not exist.")

    # If path is a file, it must be a valid epub file with a valid suffix. Then return it.
    if path.is_file() and path.suffix.lower() == EPUB_SUFFIX:
        return path

    raise ValueError(f"Invalid EPUB file '{path.name}': suffix must be '{EPUB_SUFFIX}'.")


def resolve_output(path: Path) -> Path:
    """Resolve output folder, create it if not exists and check if it is empty."""

    path = (path if path is not None else Path.cwd()).resolve()

    path.mkdir(parents=True, exist_ok=True)
    if any(path.iterdir()):
        raise RuntimeError(f"Output directory '{path}' is not empty!")

    return path
