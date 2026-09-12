#!/usr/bin/env python3
"""Executable tests for the REALMat v3 publication contract."""

from __future__ import annotations

import copy

from publication_contract import (
    ContractError,
    resolve_manifest,
    stage_for_version,
    validate_book_config,
    validate_publication_manifest,
)


def expect_contract_error(callback) -> None:
    try:
        callback()
    except ContractError:
        return
    raise AssertionError("expected ContractError")


def pdf_only_manifest() -> dict:
    return {
        "entrypoint": {
            "id": "pdf",
            "label": "PDF",
            "url": "https://github.com/projetorealmat/forallx/releases/download/v0.1.0/forallx.pdf",
        },
        "publications": [
            {
                "id": "pdf",
                "label": "PDF",
                "format": "pdf",
                "url": "https://github.com/projetorealmat/forallx/releases/download/v0.1.0/forallx.pdf",
            }
        ],
    }


def test_pdf_only_manifest_is_valid() -> None:
    validate_publication_manifest(pdf_only_manifest())


def test_html_pdf_epub_manifest_is_valid() -> None:
    manifest = {
        "entrypoint": {
            "id": "html",
            "label": "Ler no navegador",
            "url": "https://books.example.org/forallx/",
        },
        "publications": [
            {
                "id": "html",
                "label": "Ler no navegador",
                "format": "html",
                "url": "https://books.example.org/forallx/",
            },
            {
                "id": "pdf",
                "label": "PDF",
                "format": "pdf",
                "url": "https://github.com/projetorealmat/forallx/releases/download/v0.1.0/forallx.pdf",
            },
            {
                "id": "epub",
                "label": "EPUB",
                "format": "epub",
                "url": "https://books.example.org/forallx/book.epub",
            },
        ],
    }
    validate_publication_manifest(manifest)


def test_manifest_allows_non_pdf_without_format() -> None:
    manifest = pdf_only_manifest()
    manifest["publications"].insert(
        0,
        {
            "id": "html",
            "label": "Ler no navegador",
            "url": "https://books.example.org/forallx/",
        },
    )
    validate_publication_manifest(manifest)


def test_manifest_requires_canonical_pdf() -> None:
    manifest = pdf_only_manifest()
    manifest["publications"] = []
    expect_contract_error(lambda: validate_publication_manifest(manifest))


def test_manifest_rejects_duplicate_publication_ids() -> None:
    manifest = pdf_only_manifest()
    manifest["publications"].append(copy.deepcopy(manifest["publications"][0]))
    expect_contract_error(lambda: validate_publication_manifest(manifest))


def test_manifest_rejects_inconsistent_entrypoint() -> None:
    manifest = pdf_only_manifest()
    manifest["entrypoint"]["url"] = "https://example.org/other"
    expect_contract_error(lambda: validate_publication_manifest(manifest))


def test_stage_matches_version_major() -> None:
    assert stage_for_version("0.1.0") == "unreviewed"
    assert stage_for_version("1.0.0") == "reviewed"
    assert stage_for_version("2.0.0") == "adapted"
    assert stage_for_version("7.4.2") == "adapted"


def test_book_config_accepts_pdf_without_configured_url() -> None:
    config = {
        "id": "forallx",
        "title": "forallx: Lógica",
        "short_title": "forallx",
        "subject": "lógica formal",
        "build_system": "latex",
        "latex_entrypoint": "forallx.tex",
        "pdf_name": "forallx.pdf",
        "translation_stage": "unreviewed",
        "entrypoint": "pdf",
        "publications": [
            {"id": "pdf", "label": "PDF", "format": "pdf"},
        ],
    }
    validate_book_config(config)


def test_book_config_rejects_missing_pdf() -> None:
    config = {
        "id": "forallx",
        "title": "forallx: Lógica",
        "short_title": "forallx",
        "subject": "lógica formal",
        "build_system": "latex",
        "latex_entrypoint": "forallx.tex",
        "pdf_name": "forallx.pdf",
        "translation_stage": "unreviewed",
        "entrypoint": "pdf",
        "publications": [
            {"id": "html", "label": "HTML", "format": "html", "url": "https://example.org/book/"},
        ],
    }
    expect_contract_error(lambda: validate_book_config(config))


def test_resolve_manifest_builds_pdf_url_and_entrypoint_object() -> None:
    config = {
        "translation_stage": "unreviewed",
        "entrypoint": "pdf",
        "publications": [
            {"id": "pdf", "label": "PDF", "format": "pdf"},
        ],
    }
    manifest = resolve_manifest(
        config,
        repository="projetorealmat/forallx",
        tag="v0.1.0",
        pdf_name="forallx.pdf",
    )
    validate_publication_manifest(manifest)
    assert manifest["entrypoint"]["id"] == "pdf"
    assert manifest["entrypoint"]["url"].endswith("/v0.1.0/forallx.pdf")


def main() -> None:
    test_pdf_only_manifest_is_valid()
    test_html_pdf_epub_manifest_is_valid()
    test_manifest_allows_non_pdf_without_format()
    test_manifest_requires_canonical_pdf()
    test_manifest_rejects_duplicate_publication_ids()
    test_manifest_rejects_inconsistent_entrypoint()
    test_stage_matches_version_major()
    test_book_config_accepts_pdf_without_configured_url()
    test_book_config_rejects_missing_pdf()
    test_resolve_manifest_builds_pdf_url_and_entrypoint_object()
    print("publication contract verification passed")


if __name__ == "__main__":
    main()
