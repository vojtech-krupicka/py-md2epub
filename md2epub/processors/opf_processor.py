from md2epub.processors import Processor


class OpfContentProcessor(Processor):
    def run(self):
        # Render and dd content.opf
        content = self.render(
            self.env.template_dir / "content.opf.jinja",
            manifest=self.collector.manifest,
            opf=self.collector,
        )

        self.collector.set_opf(content)
