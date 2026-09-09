#!/usr/bin/env python3
"""Static contract tests for reusable REALMat book-release workflows."""

import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
COMMON_REQUIRED = (
    "id", "title", "short_title", "subject", "pdf_name", "source_prefix",
    "citation_file", "readme_file", "readme_current_block_start",
    "readme_current_block_end", "readme_version_sentence_anchor",
    "portal_repository",
)
LATEX_REQUIRED = (
    "tex_entrypoint", "build_metadata_file", "pdf_version_marker",
    "pdf_status_marker",
)
PRETEXT_REQUIRED = (
    "pretext_project_file", "pretext_pdf_target", "pretext_web_target",
)


def validate_config(config: dict) -> str:
    build_system = config.get("build_system", "latex")
    if build_system not in {"latex", "pretext"}:
        raise ValueError("build_system deve ser 'latex' ou 'pretext'.")
    required = COMMON_REQUIRED + (LATEX_REQUIRED if build_system == "latex" else PRETEXT_REQUIRED)
    missing = [key for key in required if not isinstance(config.get(key), str) or not config[key].strip()]
    if missing:
        raise ValueError(f"Configuração do livro incompleta: {', '.join(missing)}")
    if "pretext_checksum_file" in config and not isinstance(config["pretext_checksum_file"], str):
        raise ValueError("pretext_checksum_file deve ser uma string quando informado.")
    return build_system


def read_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def assert_raises(config: dict, expected: str) -> None:
    try:
        validate_config(config)
    except ValueError as error:
        assert str(error) == expected, str(error)
    else:
        raise AssertionError("A configuração deveria ser rejeitada.")


def test_config_contract() -> None:
    legacy_latex = read_fixture("book-config-latex.json")
    assert validate_config(legacy_latex) == "latex"

    minimal_pretext = read_fixture("book-config-pretext.json")
    assert validate_config(minimal_pretext) == "pretext"

    unknown = dict(minimal_pretext, build_system="html")
    assert_raises(unknown, "build_system deve ser 'latex' ou 'pretext'.")

    incomplete_latex = dict(legacy_latex)
    incomplete_latex.pop("tex_entrypoint")
    assert_raises(incomplete_latex, "Configuração do livro incompleta: tex_entrypoint")


def test_workflow_contract() -> None:
    prepare = (ROOT / ".github/workflows/book-prepare-release.yml").read_text(encoding="utf-8")
    publish = (ROOT / ".github/workflows/book-publish-release.yml").read_text(encoding="utf-8")

    for workflow in (prepare, publish):
        assert "base_branch:" in workflow
        assert "default: main" in workflow
        assert "${{ inputs.base_branch }}" in workflow

    assert 'build_system = config.get("build_system", "latex")' in prepare
    assert 'build_system = config.get("build_system", "latex")' in publish
    assert "pretext_project_file" in publish
    assert "pretext_pdf_target" in publish
    assert "pretext_web_target" in publish
    assert "pretext_checksum_file" in publish
    assert "if build_system == \"latex\"" in publish


if __name__ == "__main__":
    test_config_contract()
    test_workflow_contract()
    print("book configuration contract tests passed")
