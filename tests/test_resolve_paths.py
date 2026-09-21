"""`resolve_input` / `resolve_output`: how MANIFEST and EPUB_FILE arguments turn into real paths."""

from __future__ import annotations

from pathlib import Path

import pytest

from md2epub.commands.build import resolve_input, resolve_output

# region resolve_input


class TestResolveInput:
    @pytest.mark.parametrize("suffix", [".yml", ".yaml", ".json"])
    def test_directory_with_default_manifest(self, tmp_path: Path, suffix: str):
        manifest = tmp_path / f"manifest{suffix}"
        manifest.write_text("{}")

        assert resolve_input(tmp_path) == manifest.resolve()

    def test_none_means_current_directory(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        manifest = tmp_path / "manifest.yaml"
        manifest.write_text("{}")
        monkeypatch.chdir(tmp_path)

        assert resolve_input(None) == manifest.resolve()

    def test_relative_dot_is_resolved(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
        (tmp_path / "manifest.yml").write_text("{}")
        monkeypatch.chdir(tmp_path)

        assert resolve_input(Path(".")).parent == tmp_path.resolve()

    @pytest.mark.parametrize("name", ["book.yaml", "my-book.yml", "x.json", "BOOK.YML"])
    def test_file_with_any_name_and_valid_suffix(self, tmp_path: Path, name: str):
        manifest = tmp_path / name
        manifest.write_text("{}")

        assert resolve_input(manifest) == manifest.resolve()

    def test_file_with_invalid_suffix(self, tmp_path: Path):
        notes = tmp_path / "notes.txt"
        notes.write_text("{}")

        with pytest.raises(ValueError, match="suffix"):
            resolve_input(notes)

    def test_missing_path(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            resolve_input(tmp_path / "nope.yaml")

    def test_directory_without_manifest(self, tmp_path: Path):
        with pytest.raises(FileNotFoundError):
            resolve_input(tmp_path)

    def test_directory_ignores_files_not_named_manifest(self, tmp_path: Path):
        (tmp_path / "other.yaml").write_text("{}")

        with pytest.raises(FileNotFoundError):
            resolve_input(tmp_path)

    def test_directory_with_two_manifests_is_ambiguous(self, tmp_path: Path):
        (tmp_path / "manifest.yml").write_text("{}")
        (tmp_path / "manifest.json").write_text("{}")

        with pytest.raises(ValueError, match="Ambiguous"):
            resolve_input(tmp_path)


# region resolve_output


class TestResolveOutput:
    def test_default_is_named_after_manifest_folder(self, tmp_path: Path):
        folder = tmp_path / "my-book"
        folder.mkdir()

        assert resolve_output(folder / "manifest.yaml") == (folder / "my-book.epub").resolve()

    def test_default_is_named_after_a_custom_manifest(self, tmp_path: Path):
        assert resolve_output(tmp_path / "saga.yaml") == (tmp_path / "saga.epub").resolve()

    def test_output_directory(self, tmp_path: Path):
        out = tmp_path / "out"
        out.mkdir()

        assert resolve_output(tmp_path / "saga.yaml", out) == (out / "saga.epub").resolve()

    def test_output_directory_for_default_manifest_uses_manifest_folder_name(self, tmp_path: Path):
        folder = tmp_path / "my-book"
        out = tmp_path / "out"
        folder.mkdir()
        out.mkdir()

        assert resolve_output(folder / "manifest.yaml", out) == (out / "my-book.epub").resolve()

    def test_explicit_file_is_kept(self, tmp_path: Path):
        target = tmp_path / "custom.epub"

        assert resolve_output(tmp_path / "manifest.yaml", target) == target.resolve()

    def test_missing_suffix_is_added(self, tmp_path: Path):
        assert resolve_output(tmp_path / "manifest.yaml", tmp_path / "custom") == (tmp_path / "custom.epub").resolve()

    def test_suffix_is_case_insensitive(self, tmp_path: Path):
        target = tmp_path / "custom.EPUB"

        assert resolve_output(tmp_path / "manifest.yaml", target) == target.resolve()

    def test_wrong_suffix_is_rejected(self, tmp_path: Path):
        with pytest.raises(ValueError, match="suffix"):
            resolve_output(tmp_path / "manifest.yaml", tmp_path / "custom.zip")

    def test_custom_epub_suffix(self, tmp_path: Path):
        result = resolve_output(tmp_path / "saga.yaml", epub_suffix=".zip")

        assert result == (tmp_path / "saga.zip").resolve()

    def test_existing_output_is_protected(self, tmp_path: Path):
        target = tmp_path / "taken.epub"
        target.write_text("old")

        with pytest.raises(FileExistsError, match="--overwrite"):
            resolve_output(tmp_path / "manifest.yaml", target)

    def test_existing_output_can_be_overwritten(self, tmp_path: Path):
        target = tmp_path / "taken.epub"
        target.write_text("old")

        assert resolve_output(tmp_path / "manifest.yaml", target, overwrite=True) == target.resolve()
