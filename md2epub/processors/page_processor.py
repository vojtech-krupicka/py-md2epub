import abc
from pathlib import Path

from md2epub.core.content_collector import ContentCollector
from md2epub.core.content_creator import ContentCreator
from md2epub.models.public.page import Page
from md2epub.processors.book_processor import BookProcessor
from md2epub.processors.content_processor import ContentProcessor, HtmlInlineFile
from md2epub.types.epub_content import EpubFile, HtmlFile


class PageProcessor[TModel: Page](ContentProcessor[TModel], abc.ABC):
    """
    Base class for process page as a single unit of book content.

    There are several concrete page processors, which should take
    page model and create appropriate XHTML content (from markdown
    or jinja template or both or just include source HTML file).

    This should be achieved by convert markdown to HTML and than
    render jinja template. This final HTML content can be returned
    back to collector and from there can be added to OPF, but because
    some processors can produces more files than only HTML
    (CoverPageProcessor for example produces HTML and cover image,
    ChapterPageProcessor procudes HTML and all images in img tags)
    it is better that files are added directly to OPF and NCX.
    """

    def __init__(self, collector: ContentCollector, parent: BookProcessor, model: TModel):
        super().__init__(collector, parent, model)

        self.parent: BookProcessor = parent  # Here parent is never None, always BookProcessor
        self.toc: list = []

    def prepare(
        self,
        files: list[Path] | None = None,
        source: Path | None = None,
    ) -> tuple[Path, list[HtmlInlineFile], list[HtmlInlineFile]]:
        # Create file source path
        if not source:
            source = self.create_path()

        # Collect and resolve styles
        self.resolve_styles()
        stylesheets = self.create_relative_paths(self.collected_styles, source)

        # Collect files, add them to OPF and add create relative paths
        files = files or []
        relpath_files = []
        if files:
            collected_files = self.collect_files(files)
            relpath_files = self.create_relative_paths(collected_files, source)

        # Return tuple of source, relative stylesheets and relative files
        return source, stylesheets, relpath_files

    def finalize(self, content: str, source: Path) -> HtmlFile:
        # Create HTML file and add to OPF
        html = HtmlFile(source=source, content=content)
        self.collector.add_file(html)

        # Add to spine and guide
        if self.model.opf_spine_add:
            self.collector.add_spine(html, self.model.opf_spine_aux)
        if self.model.opf_guide_type:
            self.collector.add_guide(html, self.model.opf_guide_type, self.model.opf_guide_title)

        # Add to TOC (ncx)
        if self.model.add_to_toc and self.toc:
            for toc in self.toc:
                toc["source"] = source
                self.parent.add_toc_page(toc)

        # Add page to book processor
        self.parent.add_page(source, self.model, html)

        return html

    def create_path(self):
        """Create source path for this file"""
        parent = self.parent
        path: Path = Path(self.parent.model.name)

        while parent := parent.parent:
            path = Path(parent.model.name) / path

        return self.env.work_dir / path / f"{self.model.name}.xhtml"

    def create_relative_paths(self, files: list[EpubFile], source: Path):
        result: list[HtmlInlineFile] = []
        for file in files:
            result.append(
                HtmlInlineFile(
                    uid=file.unique_id,
                    href=file.source.relative_to(source.parent, walk_up=True).as_posix(),
                    mimetype=file.mimetype,
                )
            )

        return result

    def create_content(self, source: Path) -> str:
        creator = ContentCreator(self.collector.manifest)
        html = creator.create_from_path(source)

        return html
