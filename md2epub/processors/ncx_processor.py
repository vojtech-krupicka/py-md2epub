from md2epub.core.content_collector import ContentCollector
from md2epub.models.toc import Toc
from md2epub.processors import Processor
from md2epub.utils.filters import toc_href_filter


class NcxContentProcessor(Processor):
    def __init__(self, collector: ContentCollector, toc: Toc):
        super().__init__(collector)
        self.toc = toc

    def run(self):
        # Render and add toc.ncx
        content = self.render(
            self.env.template_dir / "toc.ncx.jinja",
            filters={"href": toc_href_filter},
            manifest=self.collector.manifest,
            work_dir=self.env.work_dir,
            toc=self.toc,
            index=0,
        )

        self.collector.set_ncx(content)
