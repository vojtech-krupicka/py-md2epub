from __future__ import annotations

from typing import TYPE_CHECKING, Any

from md2epub import current_config as config
from md2epub.processors.processor import Processor
from md2epub.utils.filters import toc_href_filter

if TYPE_CHECKING:
    from md2epub.builder import Builder

# region NcxContentProcessor
# #########################################################################


class NcxContentProcessor(Processor):
    # def __init__(self, builder: Builder, toc: Toc):
    def __init__(self, builder: Builder, toc: Any):
        super().__init__(builder)
        self.toc = toc

    def run(self):
        # Render and dd content.opf
        content = self.render(
            config.TEMPLATE_DIR / "toc.ncx.jinja",
            filters={"href": toc_href_filter},
            manifest=self.collector.manifest,
            work_dir=config.WORK_DIR,
            toc=self.toc,
            index=0,
        )

        self.collector.opf.set_ncx(content)
