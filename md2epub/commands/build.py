from __future__ import annotations

from pathlib import Path

from md2epub.core.content_collector import ContentCollector
from md2epub.core.environment import get_environment
from md2epub.models.public.manifest import Manifest
from md2epub.models.public.page import PageType
from md2epub.processors.book_processor import BookProcessor
from md2epub.processors.ncx_processor import NcxContentProcessor
from md2epub.processors.opf_processor import OpfContentProcessor
from md2epub.processors.page_processors import (
    ChapterPageProcessor,
    CoverPageProcessor,
    CustomPageProcessor,
    SubBookProcessor,
    TitlePageProcessor,
    TocPageProcessor,
)
from md2epub.types.epub import Epub
from md2epub.types.epub_content import EpubFile

MANIFEST_STEM = "manifest"
MANIFEST_SUFFIXES = (".yml", ".yaml", ".json")
EPUB_SUFFIX = ".epub"


def run(
    input_path: Path | None = None,
    output_path: Path | None = None,
    overwrite: bool = False,
) -> bool:
    """
    Run the build command.
    """

    # Get environment
    env = get_environment()
    env.logger.info(f"Running command 'build' with {input_path}, {output_path}, {overwrite} kwargs ...")

    # Resolve input path for manifest and try to instantiate it from a model
    manifest_path = resolve_input(input_path)

    # Set work_dir for build command
    env.set_work_dir(manifest_path.parent)

    # Create manifest
    manifest = Manifest.load_from_file(manifest_path)

    # Resolve output path for epub
    epub_path = resolve_output(
        manifest_path,
        output_path,
        epub_suffix=manifest.config.epub.epub_suffix,
        overwrite=overwrite,
    )

    # Collect all future content for the epub and build it
    collector = ContentCollector(manifest)
    collect(collector)
    write(collector, epub_path)

    env.logger.info(f"Command 'build' resolved paths: {manifest_path}, {epub_path}, {overwrite}.")
    return True


def collect(collector: ContentCollector) -> None:
    """
    Collect all content for the epub.

    We work over book model, collect all book's files and folders, all stylesheets
    and then prepare and render all content (pages - cover, title, chapters or subbooks)
    and finally render ncx toc file and opf content.
    """

    env = get_environment()
    env.logger.info("Collecting content for epub ...")

    # TODO: this is not added yet
    # app_default_files: list[Path] = [
    #     env.static_dir / "md2epub_stylesheet.css",
    #     env.static_dir / "md2epub_logo.png",
    # ]

    # Register page processor for all page types
    BookProcessor.register_page_processor(PageType.Cover, CoverPageProcessor)
    BookProcessor.register_page_processor(PageType.Title, TitlePageProcessor)
    BookProcessor.register_page_processor(PageType.Toc, TocPageProcessor)
    BookProcessor.register_page_processor(PageType.Chapter, ChapterPageProcessor)
    BookProcessor.register_page_processor(PageType.Custom, CustomPageProcessor)
    BookProcessor.register_page_processor(PageType.Book, SubBookProcessor)

    # First, process root book
    book_processor = BookProcessor(collector, parent=None, model=collector.manifest.book)
    book_processor.run()

    # Now we can process NCX file
    ncx_processor = NcxContentProcessor(collector, toc=book_processor.toc)
    ncx_processor.run()

    # Finally we can process Opf Content file
    opf_processor = OpfContentProcessor(collector)
    opf_processor.run()

    env.logger.info(
        f"Collected {len(list(collector.content))} files, {len(list(collector.spine))} spine items, "
        f"{len(list(collector.guide))} guide items."
    )


def write(collector: ContentCollector, output: Path):
    """Write the collected content to the epub file."""

    env = get_environment()
    env.logger.info(f"Writing collected content to epub file '{output}' ...")

    # Prepare epub object and add all files, spine and guide items
    epub = Epub()

    # Add default files (those that are not collected via content collector, but are required for epub to be valid)
    epub.add_file(env.template_dir / "mimetype", "mimetype")
    epub.add_file(env.template_dir / "container.xml", EpubFile.META_INF / "container.xml")

    # Copy all files collected in OPF manifest
    collector.copy_to_epub(epub)

    # Save output
    epub.save(output)


def resolve_input(path: Path | None) -> Path:
    """Return the resolved path to the manifest file. Its parent is the work dir."""

    # `resolve()` matters: `Path(".").name` is "" and `Path.cwd()` may be a symlink
    path = (path if path is not None else Path.cwd()).resolve()

    # Path must exist
    if not path.exists():
        raise FileNotFoundError(f"Path '{path}' does not exist.")

    # If path is a file, it must be a valid manifest file with a valid suffix. Then return it.
    if path.is_file():
        if path.suffix.lower() not in MANIFEST_SUFFIXES:
            raise ValueError(
                f"Invalid manifest file '{path.name}': suffix must be one of {'|'.join(MANIFEST_SUFFIXES)}."
            )
        return path

    # Try to find a valid manifest file in the directory. If found, return it. If not, raise.
    found = [f for suffix in MANIFEST_SUFFIXES if (f := path / f"{MANIFEST_STEM}{suffix}").is_file()]
    if not found:
        raise FileNotFoundError(f"No '{MANIFEST_STEM}' manifest ({'|'.join(MANIFEST_SUFFIXES)}) found in '{path}'.")

    # Check for ambiguity: if more than one manifest file is found, raise an error.
    if len(found) > 1:
        names = ", ".join(f.name for f in found)
        raise ValueError(f"Ambiguous manifest in '{path}': found {names}.")

    # Otherwise, return the single found file.
    return found[0]


def resolve_output(
    manifest: Path,
    output: Path | None = None,
    epub_suffix: str = EPUB_SUFFIX,
    overwrite: bool = False,
) -> Path:
    """Return the resolved path of the epub file to write."""

    # `manifest.yml` -> named after the folder, `my-book.yml` -> named after the file
    name = manifest.parent.name if manifest.stem == MANIFEST_STEM else manifest.stem

    # If output is None, set it to the manifest's parent directory. Then resolve it.
    if output is None:
        output = manifest.parent
    output = output.resolve()

    # If output is a directory, append the name with correct suffix. If output has no suffix, add correct suffix.
    # If output has a suffix that is not correct, raise an error.
    if output.is_dir():
        output /= f"{name}{epub_suffix}"
    elif not output.suffix:
        output = output.with_suffix(epub_suffix)
    elif output.suffix.lower() != epub_suffix:
        raise ValueError(f"Invalid output file '{output.name}': suffix must be '{epub_suffix}'.")

    # If output's parent directory does not exist, raise an error.
    # TODO: Consider creating the whole path if it does not exist.
    # if not output.parent.is_dir():
    #    raise FileNotFoundError(f"Output directory '{output.parent}' does not exist.")

    # If output exists and overwrite is False, raise an error.
    if output.exists() and not overwrite:
        raise FileExistsError(f"Output '{output}' already exists. Use `--overwrite` to replace it.")

    return output
