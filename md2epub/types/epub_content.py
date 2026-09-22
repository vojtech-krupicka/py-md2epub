from __future__ import annotations

import uuid
from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar, Literal
from urllib.parse import quote

from pydantic import BaseModel, Field, computed_field, model_validator

from md2epub.core.environment import get_environment
from md2epub.utils.utils import xml_id

if TYPE_CHECKING:
    from md2epub.types.epub import Epub


TValidSuffix = Literal["*"] | list[str]

# region Base class


class EpubFile(BaseModel):
    """Epub file"""

    OEBPS: ClassVar[Path] = Path("OEBPS")
    """Path inside EPUB file to store whole content inside OEBPS folder."""

    META_INF: ClassVar[Path] = Path("META-INF")
    """Path inside EPUB file to store meta informations."""

    VALID_SUFFIXES: ClassVar[TValidSuffix] = "*"
    """List of valid suffixes or '*' to match them all."""

    _FILE_COUNTER: ClassVar[int] = 0
    """Static file counter for make files unique."""

    file_num: int = 0
    """Current file number."""

    source: Path
    """Path to actual source within file system - somewhere in `Environment.work_dir` folder"""

    uid: uuid.UUID = Field(default_factory=uuid.uuid4)
    """Unique ID for this file"""

    @model_validator(mode="before")
    @classmethod
    def on_before_model_validate(cls, data: Any) -> Any:
        source: Path = data.get("source")

        if cls.VALID_SUFFIXES != "*" and source.suffix not in cls.VALID_SUFFIXES:
            raise RuntimeError(
                f"Source suffix must be any of {cls.VALID_SUFFIXES}! Actual suffix is '{source.suffix}'."
            )
        # if not source.exists():
        #     raise RuntimeError(f"Source file '{source}' doesn't exists!")

        # Set file number
        data["file_num"] = EpubFile._FILE_COUNTER
        EpubFile._FILE_COUNTER += 1

        return data

    def exists(self) -> bool:
        """Check if file actually exists (it has too, because of the model_validator!)"""
        return self.source.exists()

    def add_to_epub(self, epub: Epub):
        """Try to add file to given Epub."""
        epub.add_file(Path(self.source), Path(self.dest))

    @computed_field
    @property
    def unique_id(self) -> str:
        """Generates unique ID for this file"""
        parts = [xml_id(self.source.stem), f"{self.file_num:02}", self.uid.hex[:5]]
        return "_".join(map(str, parts))

    @computed_field
    @property
    def dest(self) -> Path:
        """Destination for most of the files inside OEPBS folder."""
        env = get_environment()
        return self.OEBPS / self.source.relative_to(env.work_dir)

    @computed_field
    @property
    def href(self) -> str:
        """Hack for display in <A> href attribute."""
        return quote(self.dest.relative_to(self.OEBPS).as_posix())

    @computed_field
    @property
    def mimetype(self) -> str:
        """Resolve mimetype of the file from its destination suffix."""

        if self.dest.suffix in [".jpg", ".jpeg"]:
            return "image/jpeg"
        elif self.dest.suffix in [".png"]:
            return "image/png"
        elif self.dest.suffix in [".gif"]:
            return "image/gif"
        elif self.dest.suffix in [".svg"]:
            return "image/svg+xml"
        elif self.dest.suffix in [".otf"]:
            return "application/x-font-opentype"
        elif self.dest.suffix in [".css"]:
            return "text/css"
        elif self.dest.suffix in [".xhtml"]:
            return "application/xhtml+xml"
        elif self.dest.suffix in [".epub"]:
            return "application/epub+zip"
        elif self.dest.suffix in [".opf"]:
            return "application/oebps-package+xml"
        elif self.dest.suffix in [".ncx"]:
            return "application/x-dtbncx+xml"
        else:
            return "application/octet-stream"

    @staticmethod
    def create_from_source(source: str | Path) -> EpubFile:
        """Create file from its source."""
        source = Path(source)

        if source.suffix in CssFile.VALID_SUFFIXES:
            return CssFile(source=source)
        elif source.suffix in ImageFile.VALID_SUFFIXES:
            return ImageFile(source=source)
        elif source.suffix in FontFile.VALID_SUFFIXES:
            return FontFile(source=source)
        elif source.suffix in TextFile.VALID_SUFFIXES:
            return TextFile(source=source)
        elif source.suffix in HtmlFile.VALID_SUFFIXES:
            return HtmlFile(source=source)
        elif source.suffix in OpfFile.VALID_SUFFIXES:
            return OpfFile(source=source)
        elif source.suffix in NcxFile.VALID_SUFFIXES:
            return NcxFile(source=source)
        else:
            return EpubFile(source=source)


# region Custom EPUB files


class CssFile(EpubFile):
    VALID_SUFFIXES: ClassVar[TValidSuffix] = [".css"]


class ImageFile(EpubFile):
    VALID_SUFFIXES: ClassVar[TValidSuffix] = [".jpg", ".jpeg", ".png", ".gif", ".svg"]


class FontFile(EpubFile):
    VALID_SUFFIXES: ClassVar[TValidSuffix] = [".otf"]


class TextFile(EpubFile):
    VALID_SUFFIXES: ClassVar[TValidSuffix] = [".txt", ".xml"]
    content: str = ""

    def add_to_epub(self, epub: Epub):
        # A plain file collected from disk (e.g. listed under `files:`) never has `content` set; a
        # generated document (a page, the OPF, the NCX) always has it explicitly passed at construction,
        # even when the rendered result happens to be an empty string.
        if "content" in self.model_fields_set:
            epub.add_text(self.content, self.dest)
        else:
            epub.add_file(self.source, self.dest)


class HtmlFile(TextFile):
    VALID_SUFFIXES: ClassVar[TValidSuffix] = [".html", ".xhtml"]

    @computed_field
    @property
    def dest(self) -> Path:
        # Chapter has '.md' suffix in manifest
        env = get_environment()
        return self.OEBPS / self.source.with_suffix(".xhtml").relative_to(env.work_dir)


class SpecialFile(TextFile):
    @computed_field
    @property
    def dest(self) -> Path:
        return self.OEBPS / self.source

    @model_validator(mode="before")
    @classmethod
    def on_before_model_validate(cls, data: Any) -> Any:
        return data


class OpfFile(SpecialFile):
    VALID_SUFFIXES: ClassVar[TValidSuffix] = [".opf"]
    source: Path = Path("content.opf")


class NcxFile(SpecialFile):
    VALID_SUFFIXES: ClassVar[TValidSuffix] = [".ncx"]
    source: Path = Path("toc.ncx")

    @computed_field
    @property
    def unique_id(self) -> str:
        return "ncx"
