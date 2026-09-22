import re
from enum import StrEnum
from pathlib import Path

from lxml import html as ehtml
from markdown import Markdown

from md2epub.core.environment import get_environment
from md2epub.models.public.config import MarkdownConfig
from md2epub.models.public.manifest import Manifest
from md2epub.utils.markdown_extensions import assert_trusted_extensions
from md2epub.utils.sanitize import sanitize_html
from md2epub.utils.utils import safe_join


class ContentType(StrEnum):
    Markdown = ".md"
    PlainText = ".txt"
    HTML = ".html"
    XHTML = ".xhtml"
    Invalid = "invalid"

    @classmethod
    def _missing_(cls, value):
        return ContentType.Invalid


class ContentCreator:
    """
    Create HTML code from its source and apply some HTML postprocessors.

    Valid inputs are:
        - file from disk
        - URL (not implemented yet)
    and valid formats are:
        - .md Markdown file will be converted using markdown library
        - .html HTML file will be converted to XHTML
        - .xhtml XHTML file will be kept same.
    """

    URI_RE = re.compile(r"^(?P<scheme>https?|ftps?):\/\/(.*)", re.MULTILINE | re.IGNORECASE)

    def __init__(self, manifest: Manifest):
        self.env = get_environment()

        self.manifest = manifest

    def create(self, text: str, content_type: ContentType) -> str:
        """
        Create from source text, returns XHTML code.
        """

        # According to content type, handle text properly
        if content_type == ContentType.Invalid:
            raise RuntimeError("Cannot create content, content-type is Invalid!")

        match content_type:
            case ContentType.Markdown:
                html = self.from_markdown(text)
                html = sanitize_html(html)
                if not html.strip():
                    return ""
            case _:
                raise RuntimeError(
                    f"Cannot create content for '{content_type.value}', create hook function is not bind!"
                )

        # Do HTML postprocess
        document = ehtml.fromstring(html)

        # TODO: some postprocess with document

        # Pretty print to XHTML
        result = ehtml.tostring(document, pretty_print=True, encoding="utf-8", method="xml")
        return result.decode("utf-8") if isinstance(result, bytes) else result

    def create_from_path(self, input: Path, encoding: str = "utf-8") -> str:
        """
        Create from input path, path can be file path or URI. Returns XHTML code.
        """

        text = ""
        content_type = ContentType.Invalid

        # Open input and read it into text
        text, content_type = self._read_uri(input, encoding) if self.is_uri(input) else self._read_file(input, encoding)

        # Create HTML code
        return self.create(text, content_type)

    def from_markdown(self, text: str) -> str:
        md = self._create_markdown()
        html = md.convert(text)

        return html

    def _create_markdown(self) -> Markdown:
        # Default config from model
        config = MarkdownConfig().model_dump()

        # Dump config from manifest to dict
        manifest_config = self.manifest.config.markdown.model_dump()

        # Join both configs and return
        config.update(manifest_config)

        # A manifest is untrusted input: it may only pick Markdown/md2epub extensions unless the build opted in
        assert_trusted_extensions(config["extensions"], trust_all=self.env.trust_extensions)

        # Create and return markdown instance
        return Markdown(**config)

    def is_uri(self, input: Path):
        """
        URI Should always starts with 'http(s)://'
        """

        if match := self.URI_RE.search(input.as_posix()):
            schema = match.group("schema")
            return schema in ("http", "https")

        return False

    def _read_uri(self, input: Path, encoding: str = "utf-8") -> tuple[str, ContentType]:
        raise NotImplementedError(f"Cannot read URI {input.as_posix()}! Not implemented yet.")

    def _read_file(self, input: Path, encoding: str = "utf-8") -> tuple[str, ContentType]:
        full_path = safe_join(self.env.work_dir, input)

        # Check if path exists
        if not full_path.exists():
            raise FileNotFoundError(f"File '{full_path}' not exists!")

        # Read input file as text
        text = full_path.read_text(encoding=encoding)

        # Remove byte order mark and other processing?
        text = text.lstrip("\ufeff")

        # Return text
        return text, ContentType(input.suffix)
