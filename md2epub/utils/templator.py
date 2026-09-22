from collections.abc import Callable
from pathlib import Path

from jinja2 import BaseLoader, FileSystemLoader
from jinja2.sandbox import SandboxedEnvironment


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

    def create_environment(self, loader: BaseLoader | None = None) -> SandboxedEnvironment:
        """
        Create the Jinja environment for every template we render.

        All output is XML/XHTML, so every value is escaped by default (`&` -> `&amp;`, `<` -> `&lt;`). A value which is
        already markup has to be marked in the template, e.g. `{{ content|safe }}`.
        """
        return SandboxedEnvironment(loader=loader, autoescape=True)

    def render(self, **kwargs):
        raise NotImplementedError(
            "Render method is not implemented in base class, please, instantiate children classes."
        )

    def _do_render(self, env: SandboxedEnvironment, template: str, **values):
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
        env = self.create_environment()
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
        env = self.create_environment(loader=FileSystemLoader(searchpath=self.search_path))
        return self._do_render(env, self.tpl_file.as_posix(), **values)
