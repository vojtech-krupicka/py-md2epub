"""The command line interface, driven through click's `CliRunner`."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner, Result

from md2epub.__main__ import cli
from tests.conftest import Project


def invoke(*args: str | Path) -> Result:
    return CliRunner().invoke(cli, [str(a) for a in args])


class TestBasics:
    def test_help(self):
        result = invoke("--help")

        assert result.exit_code == 0
        assert "build" in result.output

    def test_version(self):
        result = invoke("--version")

        assert result.exit_code == 0
        assert "version" in result.output

    def test_build_help_documents_the_arguments(self):
        result = invoke("build", "--help")

        assert result.exit_code == 0
        assert "MANIFEST" in result.output
        assert "--overwrite" in result.output


class TestBuild:
    def test_build(self, project: Project, log_cfg: Path, tmp_path: Path):
        out = tmp_path / "cli.epub"

        result = invoke("build", "--log-cfg-path", log_cfg, project.manifest_path, out)

        assert result.exit_code == 0
        assert out.is_file()

    def test_build_from_a_directory(self, project: Project, log_cfg: Path, tmp_path: Path):
        out = tmp_path / "cli.epub"

        invoke("build", "--log-cfg-path", log_cfg, project.root, out)

        assert out.is_file()

    def test_existing_output_is_kept_without_overwrite(self, project: Project, log_cfg: Path, tmp_path: Path):
        out = tmp_path / "cli.epub"
        out.write_bytes(b"old")

        invoke("build", "--log-cfg-path", log_cfg, project.manifest_path, out)

        assert out.read_bytes() == b"old"

    def test_overwrite(self, project: Project, log_cfg: Path, tmp_path: Path):
        out = tmp_path / "cli.epub"
        out.write_bytes(b"old")

        invoke("build", "--log-cfg-path", log_cfg, "--overwrite", project.manifest_path, out)

        assert out.read_bytes() != b"old"

    def test_log_config_must_exist(self, project: Project, tmp_path: Path):
        result = invoke("build", "--log-cfg-path", tmp_path / "nope.yaml", project.manifest_path)

        assert result.exit_code == 2  # click usage error

    def test_failing_build_exits_with_an_error_code(self, log_cfg: Path, tmp_path: Path):
        (tmp_path / "empty").mkdir()

        result = invoke("build", "--log-cfg-path", log_cfg, tmp_path / "empty")

        assert result.exit_code != 0

    def test_quiet_flag_still_builds(self, project: Project, log_cfg: Path, tmp_path: Path):
        out = tmp_path / "quiet.epub"

        invoke("build", "-q", "--log-cfg-path", log_cfg, project.manifest_path, out)

        assert out.is_file()

    def test_output_into_a_missing_directory(self, project: Project, log_cfg: Path, tmp_path: Path):
        out = tmp_path / "does" / "not" / "exist" / "cli.epub"

        invoke("build", "--log-cfg-path", log_cfg, project.manifest_path, out)

        assert out.is_file()
