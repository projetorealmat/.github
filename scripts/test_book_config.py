#!/usr/bin/env python3
"""Execute the embedded workflow validators against the config contract."""

import json
import os
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


def read_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def embedded_validator(workflow_name: str, step_name: str) -> str:
    workflow = (ROOT / ".github/workflows" / workflow_name).read_text(encoding="utf-8")
    step = workflow.index(f"- name: {step_name}")
    start = workflow.index("<<'PY'\n", step) + len("<<'PY'\n")
    end = workflow.index("\n          PY", start)
    return textwrap.dedent(workflow[start:end])


def run_validator(script: str, config: dict, *arguments: str) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        config_path = root / "book.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        (root / "CITATION.cff").write_text(
            'version: "0.1.0"\ndate-released: 2026-09-01\n', encoding="utf-8"
        )
        environment = dict(os.environ, GITHUB_OUTPUT=str(root / "github-output"))
        return subprocess.run(
            [sys.executable, "-", str(config_path), *arguments],
            input=script,
            text=True,
            cwd=root,
            env=environment,
            capture_output=True,
            check=False,
        )


def assert_accepted(script: str, config: dict, *arguments: str) -> None:
    result = run_validator(script, config, *arguments)
    assert result.returncode == 0, result.stderr


def assert_rejected(script: str, config: dict, expected: str, *arguments: str) -> None:
    result = run_validator(script, config, *arguments)
    assert result.returncode != 0, "A configuração deveria ser rejeitada."
    assert result.stderr.strip() == expected, result.stderr


def test_actual_config_validators() -> None:
    prepare = embedded_validator("book-prepare-release.yml", "Validar configuração, versão e data")
    publish = embedded_validator("book-publish-release.yml", "Ler configuração do livro")
    latex = read_fixture("book-config-latex.json")
    pretext = read_fixture("book-config-pretext.json")

    for validator, arguments in ((prepare, ("0.1.1", "2026-09-09")), (publish, ())):
        assert_accepted(validator, latex, *arguments)
        assert_accepted(validator, pretext, *arguments)
        assert_rejected(
            validator,
            dict(pretext, build_system="html"),
            "build_system deve ser 'latex' ou 'pretext'.",
            *arguments,
        )
        assert_rejected(
            validator,
            dict(pretext, build_system=["pretext"]),
            "build_system deve ser 'latex' ou 'pretext'.",
            *arguments,
        )
        incomplete_pretext = dict(pretext)
        incomplete_pretext.pop("pretext_pdf_target")
        assert_rejected(
            validator,
            incomplete_pretext,
            "Configuração do livro incompleta: pretext_pdf_target",
            *arguments,
        )

    incomplete_latex = dict(latex)
    incomplete_latex.pop("tex_entrypoint")
    assert_rejected(
        publish,
        incomplete_latex,
        "Configuração do livro incompleta: tex_entrypoint",
    )


if __name__ == "__main__":
    test_actual_config_validators()
    print("book configuration contract tests passed")

