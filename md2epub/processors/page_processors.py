# region CoverPageProcessor


from md2epub.models.public.page import Chapter, CoverPage, CustomPage, SubBook, TitlePage, TocPage
from md2epub.processors.page_processor import PageProcessor
from md2epub.utils.utils import extract_title, safe_join, xml_id


class CoverPageProcessor(PageProcessor[CoverPage]):
    def run(self):
        # Prepare source, stylesheets and files
        source, stylesheets, files = self.prepare([self.model.cover_image])

        # Render and add content.opf
        content = self.render(
            self.model.template_path,
            book=self.parent.model,
            stylesheets=stylesheets,
            cover_image=files[0] if files else None,
        )

        # Finalize HTML file
        self.finalize(content, source)


# region TitlePageProcessor


class TitlePageProcessor(PageProcessor[TitlePage]):
    def run(self):
        # Prepare source, stylesheets and files
        source, stylesheets, images = self.prepare(self.model.images)

        # Render and add content.opf
        content = self.render(
            self.model.template_path,
            book=self.parent.model,
            stylesheets=stylesheets,
            images=images,
            additional_content=None,
        )

        # Finalize HTML file
        self.finalize(content, source)


# region TocPageProcessor


class TocPageProcessor(PageProcessor[TocPage]):
    def run(self):
        # Prepare source, stylesheets and files
        source, stylesheets, _ = self.prepare()

        # Finalize HTML file
        html = self.finalize("", source)
        self.parent.set_toc(html, self.model, stylesheets)


# region ChapterPageProcessor


class ChapterPageProcessor(PageProcessor[Chapter]):
    def run(self):
        # Even before prepare, we need create HTML content from source
        html_content = self.create_content(self.model.source)

        # Overide name with source name
        source = safe_join(self.env.work_dir, self.model.source).with_suffix(".xhtml")

        # Prepare source, stylesheets and files
        source, stylesheets, _ = self.prepare(source=source)

        # Use the chapter's own first heading as its title, both in <title> and in the table of
        # contents; fall back to the source file name if the chapter has no heading of its own.
        title = extract_title(html_content) or self.model.source.stem
        toc_title = self.model.toc_title or title

        # Render and dd content.opf
        content = self.render(
            self.model.template_path,
            book=self.parent.model,
            stylesheets=stylesheets,
            title=title,
            content=html_content,
        )

        if self.model.add_to_toc:
            self.toc = [
                {
                    "level": self.parent.level,
                    "id": xml_id(self.model.source.stem),
                    "name": toc_title,
                    "html": toc_title,
                }
            ]

        # Finalize HTML file
        self.finalize(content, source)


# region CustomPageProcessor


class CustomPageProcessor(PageProcessor[CustomPage]):
    def run(self):
        # Prepare source, stylesheets and files
        source, stylesheets, _ = self.prepare()

        # Render and dd content.opf
        content = self.render(
            self.model.template_path,
            book=self.parent.model,
            stylesheets=stylesheets,
            values=self.model.values,
            content=None,
        )

        # Finalize HTML file
        self.finalize(content, source)


# region SubBookProcessor


class SubBookProcessor(PageProcessor[SubBook]):
    def run(self):
        from md2epub.processors.book_processor import BookProcessor

        subprocessor: BookProcessor = BookProcessor(self.collector, self.parent, self.model.book)
        subprocessor.run()
