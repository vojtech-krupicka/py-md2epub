from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent
from typing import Annotated

import yaml
from pydantic import BaseModel, Field, HttpUrl
from pydantic.json_schema import models_json_schema

from md2epub.core.environment import get_environment
from md2epub.utils.templator import FileTemplator

# region Utils


def get_doc_from_obj(obj: type[BaseModel]) -> str:
    if not obj.__doc__:
        return ""

    return dedent(obj.__doc__).strip()


def get_summary_and_description(obj: type[BaseModel]) -> tuple[str, str]:
    doc_str = get_doc_from_obj(obj)
    doc_tuple = doc_str.split("\n", maxsplit=1)

    summary = doc_tuple[0].strip() if len(doc_tuple) > 0 else ""
    description = doc_tuple[1].strip() if len(doc_tuple) > 1 else ""

    return summary, description


# region ApiDocument Models


class ApiContact(BaseModel):
    email: Annotated[str | None, Field()] = None


class ApiExternalDocs(BaseModel):
    description: str = ""
    url: HttpUrl | None = None


class ApiLicense(BaseModel):
    name: str = ""
    url: HttpUrl | None = None


class ApiInfo(BaseModel):
    title: str = ""
    description: str = ""
    version: str = ""
    contact: ApiContact = ApiContact()
    license: ApiLicense = ApiLicense()


class ApiDocument(BaseModel):
    openapi_version: Annotated[str, Field(serialization_alias="openapi")] = ""
    info: ApiInfo = ApiInfo()
    externalDocs: ApiExternalDocs = ApiExternalDocs()


# region Generator


class OpenApi:
    class Config(BaseModel):
        pass

    def __init__(self, config: Config | None = None):
        self.env = get_environment()
        self.config = config or OpenApi.Config()
        self.document = ApiDocument()
        self.components: list[type[BaseModel]] = []
        self._spec = None

    # region Document setters

    def set_api_version(self, version: str):
        self.document.openapi_version = version

    def set_title(self, title: str):
        self.document.info.title = title

    def set_app_version(self, version: str):
        self.document.info.version = version

    def set_description(self, description: str):
        self.document.info.description = description

    def set_contact(self, email: str):
        self.document.info.contact.email = email

    def set_license(self, name: str, url: str):
        self.document.info.license.name = name
        self.document.info.license.url = HttpUrl(url)

    def set_external_docs(self, description: str, url: str):
        self.document.externalDocs.description = description
        self.document.externalDocs.url = HttpUrl(url)

    def add_model(self, model: type[BaseModel]):
        self.env.logger.info(f"Add model '{model.__name__}' into OpenAPI...")
        self.components.append(model)

    # region Generation

    def generate(self, output: str | Path):
        with Path(output).open("w", encoding="utf-8") as ofp:
            ofp.write(yaml.dump(self.spec, sort_keys=False))

    def swagger(self, output: str | Path):
        template = FileTemplator(self.env.template_dir / "swagger-ui.html.jinja")
        json_spec = json.dumps(self.spec, default=str).replace("<", "\\u003c")
        content = template.render(title=self.document.info.title, openapi=json_spec)
        Path(output).write_text(content, encoding="utf-8")

    @property
    def spec(self):
        if not self._spec:
            self._spec = self.document.model_dump(mode="json", exclude_defaults=True, by_alias=True)
            self._spec["components"] = {}

            if self.components:
                self._spec["components"]["schemas"] = self._generate_schemas()

        return self._spec

    def _generate_schemas(self):
        _, schemas = models_json_schema(
            [(cls, "validation") for cls in self.components],
            ref_template="#/components/schemas/{model}",
            # ref_template="#/definitions/{model}",
        )

        return schemas.get("$defs", {})
