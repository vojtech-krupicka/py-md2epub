from __future__ import annotations

import io
import zipfile
from pathlib import Path
from typing import Self

from md2epub.utils.utils import safe_entry_name


class Epub:
    """
    Represents an EPUB file and provides methods to add content and save it.
    """

    def __init__(self):
        """Initialize an empty EPUB file with an in-memory buffer."""
        self._buffer: io.BytesIO = io.BytesIO()
        self._names: set[str] = set()

    def add_text(self, content: str, filename: str | Path) -> Self:
        """Add a text file to the EPUB.
        Args:
            content (str): The text content to add.
            filename (str | Path): The filename for the text file in the EPUB.
        Returns:
            Self: The Epub instance for method chaining.
        """

        stream = io.StringIO()
        stream.write(content)
        return self.add(filename, stream)

    def add_file(self, source: str | Path, filename: str | Path) -> Self:
        """Add a file from the filesystem to the EPUB.
        Args:
            source (str | Path): The path to the source file to add.
            filename (str | Path): The filename for the file in the EPUB.
        Returns:
            Self: The Epub instance for method chaining.
        """

        source = Path(source)
        if not source.exists():
            raise RuntimeError(f"Given source '{source}' not exists!")

        stream = io.BytesIO()
        stream.write(source.read_bytes())
        return self.add(filename, stream)

    def add(self, filename: str | Path, stream: io.BytesIO | io.StringIO) -> Self:
        """Add a file to the EPUB from a stream.
        Args:
            filename (str | Path): The filename for the file in the EPUB.
            stream (io.BytesIO | io.StringIO): The stream containing the file content.
        Returns:
            Self: The Epub instance for method chaining.
        """

        name = safe_entry_name(filename)
        if name in self._names:
            raise ValueError(f"Duplicate EPUB entry '{name}': two files would be written to the same place.")

        self._names.add(name)
        with zipfile.ZipFile(self._buffer, "a") as zip:
            zip.writestr(name, stream.getvalue())

        return self

    def save(self, dest: str | Path):
        """Save the EPUB to a file.
        Args:
            dest (str | Path): The destination path to save the EPUB file.
        """

        dest = Path(dest)
        self._buffer.seek(0)
        with dest.open("wb") as ofp:
            ofp.write(self._buffer.getvalue())

    def __len__(self) -> int:
        """Return the size of the EPUB in bytes."""
        return self._buffer.tell()
