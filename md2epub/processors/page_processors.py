# region CoverPageProcessor


from md2epub.models.public.page import Chapter, CoverPage, CustomPage, SubBook, TitlePage, TocPage
from md2epub.processors.page_processor import PageProcessor


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

        # Prepare source, stylesheets and files
        source, stylesheets, _ = self.prepare()

        # Overide name with source name
        source = source.with_stem(self.model.source.stem)

        # Render and dd content.opf
        content = self.render(
            self.model.template_path,
            book=self.parent.model,
            stylesheets=stylesheets,
            title=self.model.source.stem,
            content=html_content,
        )

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
