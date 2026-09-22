from collections import OrderedDict
from collections.abc import Iterable
from operator import attrgetter

from pydantic import BaseModel

from md2epub.core.environment import get_environment
from md2epub.models.public.manifest import Manifest
from md2epub.models.public.page import OpfGuideType
from md2epub.types.epub import Epub
from md2epub.types.epub_content import EpubFile, HtmlFile, NcxFile, OpfFile, SpecialFile


class GuideItem(BaseModel):
    """An item in the guide of the EPUB, representing a reference to a specific page or resource."""

    title: str
    type: OpfGuideType
    file: EpubFile


class SpineItem(BaseModel):
    """An item in the spine of the EPUB, representing a content document."""

    auxiliary: bool
    file: EpubFile


class ContentCollector:
    """Collects and organizes content for the EPUB based on the provided manifest."""

    def __init__(self, manifest: Manifest):
        self.env = get_environment()
        """The environment object for logging and configuration."""

        self.manifest = manifest
        """Manifest object containing the book's metadata and configuration."""

        self._content: OrderedDict[str, EpubFile] = OrderedDict()
        """Ordered dictionary to hold the content files for the EPUB, keyed by their identifiers."""

        self._spine: OrderedDict[str, SpineItem] = OrderedDict()
        """Ordered dictionary to hold the spine items for the EPUB, keyed by their identifiers."""

        self._guide: OrderedDict[str, GuideItem] = OrderedDict()
        """Ordered dictionary to hold the guide items for the EPUB, keyed by their identifiers."""

        self._opf_file: OpfFile | None = None
        """The OPF file that defines the structure and metadata of the EPUB."""

        self._ncx_file: NcxFile | None = None
        """The NCX file (XML with table of contents)."""

    @property
    def opf(self) -> OpfFile | None:
        return self._opf_file

    @property
    def ncx(self) -> NcxFile | None:
        return self._ncx_file

    @property
    def content(self) -> Iterable[EpubFile]:
        return sorted(self._content.values(), key=attrgetter("mimetype", "unique_id"))

    @property
    def spine(self) -> Iterable[SpineItem]:
        return self._spine.values()

    @property
    def guide(self) -> Iterable[GuideItem]:
        return self._guide.values()

    def set_opf(self, content: str) -> bool:
        if self._opf_file:
            self.env.logger.warning("OPF content file is already set!")
            return False

        self._opf_file = OpfFile(content=content)

        # Do not add the file to content here
        return True

    def set_ncx(self, content: str) -> bool:
        if self._ncx_file:
            self.env.logger.warning("NCX TOC file is already set!")
            return False

        self._ncx_file = NcxFile(content=content)
        self.add_file(self._ncx_file)

        return True

    def add_file(self, file: EpubFile) -> EpubFile:
        key = file.dest.as_posix()
        other = self._content.get(key)
        if other is None:
            self._content[key] = file
            return file

        # Generated files (pages, opf, ncx) come from memory, only plain copies of one source file are the "same"
        generated = isinstance(file, (HtmlFile, SpecialFile)) or isinstance(other, (HtmlFile, SpecialFile))
        if generated or other.source != file.source:
            raise ValueError(f"'{file.source}' and '{other.source}' would both be written to '{key}'.")

        return other  # the same source file listed twice: the first one wins

    def add_spine(self, file: EpubFile, aux: bool = False) -> bool:
        if file.unique_id in self._spine:
            self.env.logger.warning(f"File '{file.source}' alredy added in spine with id '{file.unique_id}'!")
            return False

        self._spine[file.unique_id] = SpineItem(file=file, auxiliary=aux)
        return True

    def add_guide(self, file: EpubFile, type: OpfGuideType, title: str) -> bool:
        if file.unique_id in self._guide:
            self.env.logger.warning(f"File '{file.source}' alredy added in guide with id '{file.unique_id}'!")
            return False

        self._guide[file.unique_id] = GuideItem(type=type, title=title, file=file)
        return True

    def copy_to_epub(self, epub: Epub):
        """Copy all collected files (in content) into the EPUB."""

        # Check if OPF file has been properly set previously
        if not self.opf:
            raise RuntimeError("OPF file has not been set in content collector!")

        # Copy all collected files from content to epub
        for file in self.content:
            file.add_to_epub(epub)

        # Let's actually add OPF file into epub
        self.opf.add_to_epub(epub)
