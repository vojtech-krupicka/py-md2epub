from __future__ import annotations

from md2epub import current_config as config
from md2epub.processors.processor import Processor

# region OpfContentProcessor


class OpfContentProcessor(Processor):
    def run(self):
        # Render and dd content.opf
        content = self.render(
            config.TEMPLATE_DIR / "content.opf.jinja",
            manifest=self.collector.manifest,
            opf=self.collector.opf,
        )

        self.collector.opf.set_content(content)
