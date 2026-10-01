from pathlib import Path

import yaml

from md2epub.core.environment import get_environment
from md2epub.models.public.book_content import Book
from md2epub.utils.utils import slugify


def run(output_dir: Path) -> bool:
    """
    Run the init command.

    Scaffolds a starter project into `output_dir`: a `chapters/`, `styles/` and `images/` folder, one
    placeholder chapter and stylesheet, and a `manifest.yaml` (cover, title and table-of-contents pages
    plus the one chapter) ready for `md2epub build` right away.
    """

    # Resolve output folder, create it if not exists and check if it is empty
    output_path = resolve_output(output_dir)

    # Lets write some folders and files
    chapters = output_path / "chapters"
    chapters.mkdir(parents=True, exist_ok=True)

    styles = output_path / "styles"
    styles.mkdir(parents=True, exist_ok=True)

    images = output_path / "images"
    images.mkdir(parents=True, exist_ok=True)

    chapter = chapters / "chapter.md"
    chapter.write_text("# Chapter 01\n\nThis is first paragraph...", encoding="utf-8")

    style = styles / "style.css"
    style.write_text(":root {\n   \n}", encoding="utf-8")

    # Now create manifest
    manifest = Book(
        **{  # noqa: PIE804
            "name": slugify(output_path.name),
            "metadata": {"title": output_path.name},
            "stylesheets": ["styles/style.css"],
            "pages": [{"type": "cover_title_toc"}, "chapters/chapter.md"],
        }
    )

    # And now export as YAML
    manifest_path = output_path / "manifest.yaml"
    with Path(manifest_path).open("w", encoding="utf-8") as ofp:
        specs = manifest.model_dump(
            mode="json",
            exclude_defaults=True,
            by_alias=True,
            exclude={"full_title", "version"},
        )
        ofp.write(yaml.safe_dump(specs, sort_keys=False))

    # No placeholder cover image is generated (would mean bundling a binary asset or an
    # image-generation dependency for something this peripheral) - point the user at the gap instead,
    # since `manifest.yaml` already references one and a silently imageless cover is easy to miss.
    get_environment().logger.info(
        f"Add a cover image at '{images / 'cover.jpg'}' before building - the manifest's cover page expects one there."
    )

    return True


def resolve_output(path: Path) -> Path:
    """Resolve output folder, create it if not exists and check if it is empty."""

    path = (path if path is not None else Path.cwd()).resolve()

    path.mkdir(parents=True, exist_ok=True)
    if any(path.iterdir()):
        raise RuntimeError(f"Output directory '{path}' is not empty!")

    return path
