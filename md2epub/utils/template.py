from pathlib import Path

from jinja2 import BaseLoader, Environment, FileSystemLoader, Template


class TemplateBase:
    def __init__(self, filters: dict[str, callable] | None = None):
        # Default filters
        self.filters = {}

        if filters:
            self.filters.update(filters)

    def register_filter(self, name: str, callback: callable):
        self.filters[name] = callback

    def register_filters(self, filters: dict[str, callable]):
        self.filters.update(filters)

    def render(self, **kwargs):
        raise NotImplementedError(
            "Render method is not implemented in base class, please, instantiate children classes."
        )

    def _do_render(self, env: Environment, template: str | Template, **values):
        # Prepare filters
        env.filters.update(self.filters)

        # Get template from file or string
        tpl = env.get_template(template)

        # Render tempate with given values
        return tpl.render(**values)


class StringTemplate(TemplateBase):
    def __init__(self, text: str, filters: dict[str, callable] | None = None):
        super().__init__(filters)
        self.tpl_string = text

    def render(self, **values):
        env = Environment(loader=BaseLoader)
        return self._do_render(env, self.tpl_string, **values)


class FileTemplate(TemplateBase):
    def __init__(
        self,
        tpl_file: Path,
        search_path: Path | None = None,
        filters: dict[str, callable] | None = None,
    ):
        super().__init__(filters)

        # If not search path is set, it get it form template file as parent folder
        if not search_path:
            search_path = tpl_file.parent.absolute()
            tpl_file = tpl_file.name

        self.tpl_file = tpl_file
        self.search_path = search_path

    def render(self, **values):
        env = Environment(loader=FileSystemLoader(searchpath=self.search_path))
        return self._do_render(env, self.tpl_file, **values)
