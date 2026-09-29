"""`unpack`: extract an existing EPUB back into loose files on disk."""

from __future__ import annotations

import zipfile
from pathlib import Path

import pytest

from md2epub.commands import unpack
from tests.conftest import Project
from tests.test_cli import invoke


class TestUnpackCommand:
    def test_unpacks_every_file_from_the_epub(self, project: Project, tmp_path: Path):
        epub_path = project.build()
        out = tmp_path / "unpacked"

        unpack.run(epub_path, out)

        with zipfile.ZipFile(epub_path) as epub:
            for name in epub.namelist():
                if not name.endswith("/"):
                    assert (out / name).is_file(), name

    def test_unpacked_content_matches_the_epub(self, project: Project, tmp_path: Path):
        epub_path = project.build()
        out = tmp_path / "unpacked"

        unpack.run(epub_path, out)

        with zipfile.ZipFile(epub_path) as epub:
            assert (out / "OEBPS/content.opf").read_bytes() == epub.read("OEBPS/content.opf")
            assert (out / "mimetype").read_bytes() == epub.read("mimetype")

    def test_missing_epub_is_rejected(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            unpack.run(tmp_path / "does-not-exist.epub", tmp_path / "out")

    def test_wrong_suffix_is_rejected(self, tmp_path: Path):
        not_an_epub = tmp_path / "notes.txt"
        not_an_epub.write_text("hello")

        with pytest.raises(ValueError, match="suffix"):
            unpack.run(not_an_epub, tmp_path / "out")

    @pytest.mark.parametrize("suffix", ["", ".e", ".ep"])
    def test_truncated_suffix_is_rejected(self, tmp_path: Path, suffix: str):
        """Regression: `suffix in EPUB_SUFFIX` used to accept any substring of `.epub`, including none at all."""
        fake = tmp_path / f"book{suffix}"
        fake.write_bytes(b"not actually a zip")

        with pytest.raises(ValueError, match="suffix"):
            unpack.run(fake, tmp_path / "out")

    def test_output_directory_is_created(self, project: Project, tmp_path: Path):
        epub_path = project.build()
        out = tmp_path / "does" / "not" / "exist" / "yet"

        unpack.run(epub_path, out)

        assert out.is_dir()
        assert (out / "mimetype").is_file()

    def test_non_empty_output_directory_is_rejected(self, project: Project, tmp_path: Path):
        epub_path = project.build()
        out = tmp_path / "unpack-out"
        out.mkdir()
        (out / "existing.txt").write_text("already here")

        with pytest.raises(RuntimeError, match="not empty"):
            unpack.run(epub_path, out)


class TestUnpackCli:
    def test_input_epub_is_required(self):
        result = invoke("unpack")

        assert result.exit_code != 0
        assert "input-epub" in result.output or "Missing option" in result.output

    def test_cli_round_trip(self, project: Project, tmp_path: Path, log_cfg: Path):
        epub_path = project.build()
        out = tmp_path / "unpacked"

        result = invoke("unpack", "--log-cfg-path", log_cfg, "-i", epub_path, "-o", out)

        assert result.exit_code == 0, result.output
        assert (out / "OEBPS" / "content.opf").is_file()
