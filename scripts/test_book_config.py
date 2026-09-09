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


def workflow_call_input_default(workflow: str, input_name: str) -> str:
    lines = workflow.splitlines()
    try:
        workflow_call = lines.index("  workflow_call:")
        inputs = lines.index("    inputs:", workflow_call)
    except ValueError as error:
        raise AssertionError("workflow_call não declara inputs.") from error

    input_header = f"      {input_name}:"
    try:
        start = lines.index(input_header, inputs)
    except ValueError as error:
        raise AssertionError(f"workflow_call não declara o input {input_name}.") from error

    for line in lines[start + 1 :]:
        if line.startswith("    ") and line.strip().endswith(":"):
            break
        if line.startswith("        default: "):
            return line.removeprefix("        default: ").strip()
    raise AssertionError(f"input {input_name} não declara default.")


def assert_contains(workflow: str, expected: str, description: str) -> None:
    assert expected in workflow, f"{description}: esperado {expected!r}"


def assert_base_branch_contract(prepare: str, publish: str) -> None:
    assert workflow_call_input_default(prepare, "base_branch") == "main"
    assert workflow_call_input_default(publish, "base_branch") == "main"

    expression = "${{ inputs.base_branch }}"
    assert_contains(prepare, f"ref: {expression}", "prepare checkout usa base_branch")
    assert_contains(prepare, f'--base "{expression}"', "prepare cria PR na base configurada")
    assert_contains(publish, f"ref: {expression}", "publish faz checkout da base configurada")
    assert_contains(publish, f"BASE_BRANCH: {expression}", "publish recebe base_branch")
    assert_contains(
        publish,
        '[[ "${base_ref}" == "${BASE_BRANCH}" ]]',
        "publish valida a base da Release PR",
    )
    assert_contains(
        publish,
        '"origin/${BASE_BRANCH}"',
        "publish verifica ancestralidade na base configurada",
    )


def assert_contract_failure(prepare: str, publish: str) -> None:
    try:
        assert_base_branch_contract(prepare, publish)
    except AssertionError:
        return
    raise AssertionError("A mutação deveria violar o contrato de base_branch.")


def replace_once(workflow: str, previous: str, replacement: str) -> str:
    assert workflow.count(previous) == 1, f"Mutação ambígua ou ausente: {previous!r}"
    return workflow.replace(previous, replacement, 1)


def test_base_branch_contract() -> None:
    prepare = (ROOT / ".github/workflows/book-prepare-release.yml").read_text(encoding="utf-8")
    publish = (ROOT / ".github/workflows/book-publish-release.yml").read_text(encoding="utf-8")
    expression = "${{ inputs.base_branch }}"

    assert_base_branch_contract(prepare, publish)
    assert_contract_failure(replace_once(prepare, "default: main", "default: master"), publish)
    assert_contract_failure(prepare, replace_once(publish, "default: main", "default: master"))
    assert_contract_failure(replace_once(prepare, f"ref: {expression}", "ref: main"), publish)
    assert_contract_failure(
        replace_once(prepare, f'--base "{expression}"', "--base main"),
        publish,
    )
    assert_contract_failure(prepare, replace_once(publish, f"ref: {expression}", "ref: main"))
    assert_contract_failure(
        prepare,
        replace_once(publish, f"BASE_BRANCH: {expression}", "BASE_BRANCH: main"),
    )
    assert_contract_failure(
        prepare,
        replace_once(
            publish,
            '[[ "${base_ref}" == "${BASE_BRANCH}" ]]',
            '[[ "${base_ref}" == "main" ]]',
        ),
    )
    assert_contract_failure(
        prepare,
        replace_once(publish, '"origin/${BASE_BRANCH}"', '"origin/main"'),
    )


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
    test_base_branch_contract()
    test_actual_config_validators()
    print("book configuration contract tests passed")

