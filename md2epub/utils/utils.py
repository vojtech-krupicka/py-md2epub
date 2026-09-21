from pathlib import Path, PurePosixPath, PureWindowsPath


def safe_join(root: Path, rel: Path) -> Path:
    p = (root / rel).resolve()  # absolute rel discards root; resolve() follows symlinks
    if not p.is_relative_to(root.resolve()):
        raise ValueError(f"'{rel}' escapes the project directory")
    return p


def safe_entry_name(filename: str | Path) -> str:
    """
    Validate and normalize the name of an entry inside the EPUB (a zip archive).

    Entry names must be relative and must stay inside the archive, otherwise a program extracting the
    EPUB without its own checks could write outside of the target folder (zip-slip).

    Raises:
        ValueError: if the name is empty, absolute, contains `..`, a drive letter or a NUL byte.
    """

    # Zip entries always use "/", treat a backslash as a separator too so "a\..\b" is caught on every OS
    name = str(filename).replace("\\", "/")
    path = PurePosixPath(name)

    if not path.parts or path.is_absolute() or ".." in path.parts or "\x00" in name or PureWindowsPath(name).drive:
        raise ValueError(f"Unsafe EPUB entry name {str(filename)!r}: must be a relative path inside the archive.")

    return path.as_posix()
