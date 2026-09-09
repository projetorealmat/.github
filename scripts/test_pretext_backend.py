#!/usr/bin/env python3
"""Regression tests for the deterministic PreTeXt build-output validator."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "scripts" / "validate_pretext_output.py"
WORKFLOW = ROOT / ".github" / "workflows" / "book-build-pretext.yml"
PUBLISH_WORKFLOW = ROOT / ".github" / "workflows" / "book-publish-release.yml"
FIXTURE = ROOT / "tests" / "fixtures" / "pretext-build-config.json"


def run_validator(pdf_count: int, *, version_text: str = "Versão: v0.1.1") -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        pdf_dir = root / "output" / "print"
        pdf_dir.mkdir(parents=True)
        for index in range(pdf_count):
            (pdf_dir / f"candidate-{index}.pdf").write_bytes(b"not-empty")
        web_dir = root / "output" / "web"
        web_dir.mkdir(parents=True)
        (web_dir / "index.html").write_text("<html></html>", encoding="utf-8")
        bin_dir = root / "bin"
        bin_dir.mkdir()
        pdftotext = bin_dir / "pdftotext"
        pdftotext.write_text(
            "#!/usr/bin/env sh\nprintf '%s\\nStatus: em revisão\\n' '" + version_text + "'\n",
            encoding="utf-8",
        )
        pdftotext.chmod(0o755)
        output = root / "release" / "aata.pdf"
        environment = dict(os.environ, PATH=f"{bin_dir}:{os.environ['PATH']}")
        return subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--pdf-dir", str(pdf_dir), "--pdf-output", str(output),
                "--web-dir", str(web_dir), "--release-tag", "v0.1.1",
                "--release-status", "em revisão", "--version-marker", "Versão: ",
                "--status-marker", "Status: ",
            ],
            text=True, env=environment, capture_output=True, check=False,
        )


def test_accepts_one_pdf_and_normalizes_its_name() -> None:
    result = run_validator(1)
    assert result.returncode == 0, result.stderr


def test_rejects_ambiguous_pdf_output() -> None:
    result = run_validator(2)
    assert result.returncode != 0
    assert "Esperado exatamente um PDF" in result.stderr


def test_rejects_missing_pdf_output() -> None:
    result = run_validator(0)
    assert result.returncode != 0
    assert "Esperado exatamente um PDF" in result.stderr


def test_rejects_missing_version_marker() -> None:
    result = run_validator(1, version_text="Versão: v0.1.0")
    assert result.returncode != 0
    assert "marcador de versão" in result.stderr


def test_reusable_workflow_keeps_pretext_outputs_deterministic() -> None:
    workflow = WORKFLOW.read_text(encoding="utf-8")
    config = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert "workflow_call:" in workflow
    for name in ("release_commit:", *[f"{name}:" for name in config]):
        assert name in workflow
    assert 'pretext build --clean "${PRETEXT_PDF_TARGET}"' in workflow
    assert 'pretext build --clean "${PRETEXT_WEB_TARGET}"' in workflow
    assert "--pdf-dir" in workflow
    assert "pretext-release-pdf" in workflow
    assert "pretext-release-web" in workflow


def test_publisher_waits_for_pretext_build_before_releasing() -> None:
    workflow = PUBLISH_WORKFLOW.read_text(encoding="utf-8")
    assert "build-pretext:" in workflow
    assert "uses: ./.github/workflows/book-build-pretext.yml" in workflow
    assert "release-pretext:" in workflow
    assert "needs: [resolve, build-pretext]" in workflow
    assert 'if: needs.resolve.outputs.build_system == \'pretext\'' in workflow
    assert "actions/download-artifact@" in workflow
    assert "pretext-release-pdf" in workflow
    assert 'release_pdf="pretext-release-assets/${PDF_NAME}"' in workflow
    assert 'sha256sum "${release_pdf}"' in workflow
    assert 'printf \'%s  %s\\n\' "${pdf_checksum}" "${PDF_NAME}" > SHA256SUMS' in workflow
    assert "Verificar PDF publicado contra artefato PreTeXt validado" in workflow
    assert "O PDF publicado diverge do artefato PreTeXt validado." in workflow
    assert "pretext_requirements_file: ${{ needs.resolve.outputs.pretext_requirements_file }}" in workflow


if __name__ == "__main__":
    test_accepts_one_pdf_and_normalizes_its_name()
    test_rejects_ambiguous_pdf_output()
    test_rejects_missing_pdf_output()
    test_rejects_missing_version_marker()
    test_reusable_workflow_keeps_pretext_outputs_deterministic()
    test_publisher_waits_for_pretext_build_before_releasing()
    print("pretext backend tests passed")
