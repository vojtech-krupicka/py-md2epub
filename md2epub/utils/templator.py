from collections.abc import Callable
from pathlib import Path

from jinja2 import Environment, FileSystemLoader


class Templator:
    def __init__(self, filters: dict[str, Callable] | None = None):
        # Default filters
        self.filters = {}

        if filters:
            self.filters.update(filters)

    def register_filter(self, name: str, callback: Callable):
        self.filters[name] = callback

    def register_filters(self, filters: dict[str, Callable]):
        self.filters.update(filters)

    def render(self, **kwargs):
        raise NotImplementedError(
            "Render method is not implemented in base class, please, instantiate children classes."
        )

    def _do_render(self, env: Environment, template: str, **values):
        # Prepare filters
        env.filters.update(self.filters)

        # Get template from file or string
        tpl = env.get_template(template)

        # Render tempate with given values
        return tpl.render(**values)


class StringTemplator(Templator):
    def __init__(
        self,
        text: str,
        filters: dict[str, Callable] | None = None,
    ):
        super().__init__(filters)
        self.tpl_string = text

    def render(self, **values):
        env = Environment()
        return self._do_render(env, self.tpl_string, **values)


class FileTemplator(Templator):
    def __init__(
        self,
        tpl_file: Path,
        search_path: Path | None = None,
        filters: dict[str, Callable] | None = None,
    ):
        super().__init__(filters)

        if not search_path:
            search_path = tpl_file.parent.absolute()
            tpl_file = Path(tpl_file.name)

        self.tpl_file = tpl_file
        self.search_path = search_path

    def render(self, **values):
        env = Environment(loader=FileSystemLoader(searchpath=self.search_path))
        return self._do_render(env, self.tpl_file.as_posix(), **values)
