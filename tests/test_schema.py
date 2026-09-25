"""The `schema` command: an OpenAPI document of the manifest models plus a Swagger UI page."""

from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

from tests.test_cli import invoke


@pytest.fixture
def generated(tmp_path: Path, log_cfg: Path) -> Path:
    out = tmp_path / "schema" / "nested"
    result = invoke("schema", "--log-cfg-path", log_cfg, "-o", out)

    assert result.exit_code == 0, result.output
    return out


def test_writes_both_files_and_creates_the_directory(generated: Path):
    assert (generated / "openapi.yaml").is_file()
    assert (generated / "swagger-ui.html").is_file()


def test_document_describes_the_manifest(generated: Path):
    doc = yaml.safe_load((generated / "openapi.yaml").read_text(encoding="utf-8"))

    assert doc["openapi"].startswith("3.")
    assert doc["info"]["description"] != "Some description"
    assert {"Manifest", "Book", "Chapter", "Config"} <= set(doc["components"]["schemas"])


def test_every_ref_resolves(generated: Path):
    text = (generated / "openapi.yaml").read_text(encoding="utf-8")
    schemas = yaml.safe_load(text)["components"]["schemas"]

    assert set(re.findall(r"#/components/schemas/(\w+)", text)) <= set(schemas)


def test_fields_carry_their_documentation(generated: Path):
    schemas = yaml.safe_load((generated / "openapi.yaml").read_text(encoding="utf-8"))["components"]["schemas"]

    for name, schema in schemas.items():
        for field, definition in schema.get("properties", {}).items():
            assert definition.get("description") or "$ref" in definition, f"{name}.{field} has no description"


def test_output_is_deterministic(tmp_path: Path, log_cfg: Path):
    for name in ("a", "b"):
        assert invoke("schema", "--log-cfg-path", log_cfg, "-o", tmp_path / name).exit_code == 0

    assert (tmp_path / "a" / "openapi.yaml").read_text() == (tmp_path / "b" / "openapi.yaml").read_text()


def test_swagger_page_cannot_be_broken_out_of(generated: Path):
    html = (generated / "swagger-ui.html").read_text(encoding="utf-8")
    spec = html.split("spec:", 1)[1].split("dom_id", 1)[0]

    assert "</" not in spec
    assert "<!--" not in spec
