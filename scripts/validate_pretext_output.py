#!/usr/bin/env python3
"""Validate and normalize the outputs produced by a PreTeXt target."""

from __future__ import annotations

import argparse
import shutil
import subprocess
from pathlib import Path


def fail(message: str) -> None:
    raise SystemExit(message)


def exactly_one_pdf(pdf_dir: Path) -> Path:
    if not pdf_dir.is_dir():
        fail(f"Diretório de saída PDF inexistente: {pdf_dir}")
    candidates = sorted(path for path in pdf_dir.rglob("*.pdf") if path.is_file())
    if len(candidates) != 1:
        listed = ", ".join(str(path) for path in candidates) or "nenhum arquivo"
        fail(
            "Esperado exatamente um PDF na saída PreTeXt "
            f"{pdf_dir}; encontrados {len(candidates)}: {listed}"
        )
    return candidates[0]


def pdf_text(pdf: Path) -> str:
    try:
        result = subprocess.run(
            ["pdftotext", "-layout", str(pdf), "-"],
            check=True,
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        fail("pdftotext é necessário para validar o PDF PreTeXt.")
    except subprocess.CalledProcessError as error:
        fail(f"Não foi possível extrair texto do PDF {pdf}: {error.stderr.strip()}")
    return result.stdout


def validate_marker(text: str, marker: str, expected: str, label: str) -> None:
    if marker and f"{marker}{expected}" not in text:
        fail(f"O PDF não contém o marcador de {label} esperado: {marker}{expected}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf-dir", required=True, type=Path)
    parser.add_argument("--pdf-output", required=True, type=Path)
    parser.add_argument("--web-dir", required=True, type=Path)
    parser.add_argument("--release-tag", required=True)
    parser.add_argument("--release-status", required=True)
    parser.add_argument("--version-marker", default="")
    parser.add_argument("--status-marker", default="")
    arguments = parser.parse_args()

    source_pdf = exactly_one_pdf(arguments.pdf_dir)
    if source_pdf.stat().st_size == 0:
        fail(f"O PDF PreTeXt está vazio: {source_pdf}")
    if not arguments.web_dir.is_dir() or not (arguments.web_dir / "index.html").is_file():
        fail(f"A saída web PreTeXt não contém index.html: {arguments.web_dir}")

    arguments.pdf_output.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_pdf, arguments.pdf_output)
    text = pdf_text(arguments.pdf_output)
    validate_marker(text, arguments.version_marker, arguments.release_tag, "versão")
    validate_marker(text, arguments.status_marker, arguments.release_status, "status")


if __name__ == "__main__":
    main()
