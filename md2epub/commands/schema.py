from pathlib import Path

from pydantic import BaseModel

from md2epub.core.environment import get_environment
from md2epub.models.public.manifest import Manifest
from md2epub.models.public.page import BookContent
from md2epub.utils.openapi import OpenApi


def run(output_dir: Path):
    env = get_environment()

    openapi = OpenApi()

    openapi.set_api_version("3.1.0")
    openapi.set_app_version(env.get_version())
    openapi.set_title("Markdown 2 ePub convertor")
    openapi.set_description(
        "Reference for the `md2epub` manifest: the YAML or JSON file that describes a book and how to build it "
        "into an EPUB.\n\n"
        "The schemas below document every manifest field, including the page types (`cover`, `title`, `toc`, "
        "`chapter`, `custom`, `subbook`) that make up the book. `Manifest` is the top-level document, so start there.\n\n"
        "This is a description of the manifest file format, not a web API: there are no endpoints, only schemas. "
        "It is generated from the models with `md2epub schema`."
    )
    openapi.set_contact("voker@email.cz")
    openapi.set_license("MIT", "https://mit-license.org/")
    openapi.set_external_docs("GitHub", "https://github.com/vojtech-krupicka/py-md2epub")

    for model in [Manifest, BookContent] + get_subclasses(BookContent):
        openapi.add_model(model)

    output_dir.mkdir(parents=True, exist_ok=True)
    openapi.generate(output_dir / Path("openapi.yaml"))
    openapi.swagger(output_dir / Path("swagger-ui.html"))


def get_subclasses(cls: type[BaseModel]) -> list[type[BaseModel]]:
    subclasses = set()
    work = [cls]
    while work:
        parent = work.pop()
        for child in parent.__subclasses__():
            if child not in subclasses:
                subclasses.add(child)
                work.append(child)
    return list(subclasses)
