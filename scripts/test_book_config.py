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


def run_validator(
    script: str,
    config: dict,
    *arguments: str,
    citation: str = 'version: "0.1.0"\ndate-released: 2026-09-01\n',
) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        config_path = root / "book.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        (root / "CITATION.cff").write_text(citation, encoding="utf-8")
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


def run_citation_update(citation: str) -> tuple[subprocess.CompletedProcess[str], str]:
    script = embedded_validator("book-prepare-release.yml", "Atualizar CITATION.cff e README")
    config = read_fixture("book-config-pretext.json")
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        config_path = root / "book.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        citation_path = root / "CITATION.cff"
        citation_path.write_text(citation, encoding="utf-8")
        (root / "README.md").write_text(
            "<!-- release-pdf-current:start -->\n"
            "- Ainda não há PDF.\n"
            "<!-- release-pdf-current:end -->\n"
            "A versão atualmente recomendada é uma prévia.\n",
            encoding="utf-8",
        )
        result = subprocess.run(
            [sys.executable, "-", str(config_path), "0.1.1", "2026-09-09"],
            input=script,
            text=True,
            cwd=root,
            env=dict(os.environ, GITHUB_REPOSITORY="projetorealmat/aata"),
            capture_output=True,
            check=False,
        )
        return result, citation_path.read_text(encoding="utf-8")


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

    unsafe_pretext_values = (
        ("pdf_name", "../escape.pdf", "pdf_name deve ser um nome de arquivo simples e seguro."),
        ("pdf_name", "aata-*.pdf", "pdf_name deve ser um nome de arquivo simples e seguro."),
        ("pdf_name", "aata?.pdf", "pdf_name deve ser um nome de arquivo simples e seguro."),
        ("pdf_name", "aata[0].pdf", "pdf_name deve ser um nome de arquivo simples e seguro."),
        ("pdf_name", "aata].pdf", "pdf_name deve ser um nome de arquivo simples e seguro."),
        ("pretext_project_file", "../project.ptx", "pretext_project_file deve ser um caminho relativo e seguro."),
        ("pretext_pdf_target", "../print", "pretext_pdf_target deve ser um nome de alvo seguro."),
        ("pretext_web_target", "-web", "pretext_web_target deve ser um nome de alvo seguro."),
        ("pretext_requirements_file", "../requirements.txt", "pretext_requirements_file deve ser um caminho relativo e seguro."),
        ("pretext_checksum_file", "../checksum", "pretext_checksum_file deve ser um caminho relativo e seguro."),
    )
    for key, value, expected in unsafe_pretext_values:
        for validator, arguments in ((prepare, ("0.1.1", "2026-09-09")), (publish, ())):
            assert_rejected(validator, dict(pretext, **{key: value}), expected, *arguments)

    for validator, arguments in ((prepare, ("0.1.1", "2026-09-09")), (publish, ())):
        assert_rejected(
            validator,
            dict(pretext, pretext_checksum_file=None),
            "pretext_checksum_file deve ser uma string quando informado.",
            *arguments,
        )


def test_prepare_initial_validation_accepts_citation_without_date() -> None:
    prepare = embedded_validator("book-prepare-release.yml", "Validar configuração, versão e data")
    result = run_validator(
        prepare,
        read_fixture("book-config-pretext.json"),
        "0.1.1",
        "2026-09-09",
        citation='version: "0.1.0"\n',
    )
    assert result.returncode == 0, result.stderr


def test_prepare_update_inserts_missing_citation_date() -> None:
    result, updated = run_citation_update('version: "0.1.0"\n')
    assert result.returncode == 0, result.stderr
    assert 'version: "0.1.1"' in updated
    assert updated.count("date-released: 2026-09-09") == 1


def test_prepare_update_replaces_existing_citation_date() -> None:
    result, updated = run_citation_update(
        'version: "0.1.0"\ndate-released: 2026-01-01\n'
    )
    assert result.returncode == 0, result.stderr
    assert updated.count("date-released: 2026-09-09") == 1
    assert "date-released: 2026-01-01" not in updated


def test_prepare_update_rejects_multiple_citation_dates() -> None:
    result, _ = run_citation_update(
        'version: "0.1.0"\ndate-released: 2026-01-01\ndate-released: 2026-02-01\n'
    )
    assert result.returncode != 0
    assert "date-released" in result.stderr


if __name__ == "__main__":
    test_base_branch_contract()
    test_actual_config_validators()
    test_prepare_initial_validation_accepts_citation_without_date()
    test_prepare_update_inserts_missing_citation_date()
    test_prepare_update_replaces_existing_citation_date()
    test_prepare_update_rejects_multiple_citation_dates()
    print("book configuration contract tests passed")
