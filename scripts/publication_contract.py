#!/usr/bin/env python3
"""Validation and resolution helpers for the REALMat v3 publication contract."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


STAGES = frozenset({"unreviewed", "reviewed", "adapted"})
PUBLICATION_ID = re.compile(r"[a-z0-9][a-z0-9-]*\Z")
VERSION = re.compile(r"v?(\d+)\.(\d+)\.(\d+)\Z")
REPOSITORY = re.compile(r"[^/\s]+/[^/\s]+\Z")
SAFE_FILENAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")


class ContractError(ValueError):
    """Raised when a book config or publication manifest violates the contract."""


def _require_mapping(value: object, field: str) -> dict:
    if not isinstance(value, dict):
        raise ContractError(f"{field} deve ser um objeto JSON.")
    return value


def _require_string(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} deve ser uma string não vazia.")
    return value


def _validate_id(value: object, field: str) -> str:
    value = _require_string(value, field)
    if PUBLICATION_ID.fullmatch(value) is None:
        raise ContractError(f"{field} inválido.")
    return value


def _validate_url(value: object, field: str) -> str:
    value = _require_string(value, field)
    if any(character.isspace() for character in value):
        raise ContractError(f"{field} não pode conter espaços.")
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ContractError(f"{field} deve ser uma URL HTTP(S).")
    return value


def _validate_stage(value: object, field: str = "translation_stage") -> str:
    value = _require_string(value, field)
    if value not in STAGES:
        raise ContractError(f"{field} inválido: {value}.")
    return value


def stage_for_version(version: str) -> str:
    """Return the editorial stage represented by a semantic version."""

    if not isinstance(version, str):
        raise ContractError("version deve ser uma string semver.")
    match = VERSION.fullmatch(version)
    if match is None:
        raise ContractError("version deve seguir MAJOR.MINOR.PATCH.")
    major = int(match.group(1))
    if major == 0:
        return "unreviewed"
    if major == 1:
        return "reviewed"
    return "adapted"


def _validate_publications(
    publications: object,
    *,
    require_pdf_url: bool,
) -> list[dict]:
    if not isinstance(publications, list) or not publications:
        raise ContractError("publications deve ser uma lista não vazia.")

    normalized: list[dict] = []
    seen: set[str] = set()
    for index, publication_value in enumerate(publications):
        field = f"publications[{index}]"
        publication = _require_mapping(publication_value, field)
        publication_id = _validate_id(publication.get("id"), f"{field}.id")
        if publication_id in seen:
            raise ContractError(f"id de publicação duplicado: {publication_id}.")
        seen.add(publication_id)
        label = _require_string(publication.get("label"), f"{field}.label")
        format_value = publication.get("format")
        if publication_id == "pdf":
            format_name = _require_string(format_value, f"{field}.format")
            if format_name != "pdf":
                raise ContractError("A publicação id=pdf deve ter format=pdf.")
        elif format_value is None:
            format_name = None
        else:
            format_name = _require_string(format_value, f"{field}.format")

        has_url = "url" in publication and publication["url"] is not None
        if publication_id == "pdf" and not require_pdf_url and not has_url:
            url = None
        else:
            url = _validate_url(publication.get("url"), f"{field}.url")

        normalized_publication = {
            "id": publication_id,
            "label": label,
        }
        if format_name is not None:
            normalized_publication["format"] = format_name
        if url is not None:
            normalized_publication["url"] = url
        normalized.append(normalized_publication)
    return normalized


def validate_publication_manifest(manifest: object) -> dict:
    """Validate a resolved manifest emitted in a release event."""

    manifest = _require_mapping(manifest, "manifest")
    entrypoint = _require_mapping(manifest.get("entrypoint"), "entrypoint")
    entrypoint_id = _validate_id(entrypoint.get("id"), "entrypoint.id")
    entrypoint_label = _require_string(entrypoint.get("label"), "entrypoint.label")
    entrypoint_url = _validate_url(entrypoint.get("url"), "entrypoint.url")
    publications = _validate_publications(manifest.get("publications"), require_pdf_url=True)

    pdf_publications = [publication for publication in publications if publication["id"] == "pdf"]
    if len(pdf_publications) != 1:
        raise ContractError("O manifesto deve conter exatamente uma publicação PDF canônica.")
    if "url" not in pdf_publications[0]:
        raise ContractError("A publicação PDF canônica deve ter uma URL final.")

    by_id = {publication["id"]: publication for publication in publications}
    if entrypoint_id not in by_id:
        raise ContractError("entrypoint.id deve apontar para uma publicação.")
    if by_id[entrypoint_id]["url"] != entrypoint_url:
        raise ContractError("entrypoint.url deve ser igual à URL da publicação escolhida.")
    if by_id[entrypoint_id]["label"] != entrypoint_label:
        raise ContractError("entrypoint.label deve ser igual ao rótulo da publicação escolhida.")

    if "translation_stage" in manifest:
        _validate_stage(manifest["translation_stage"])
    return manifest


def validate_book_config(config: object) -> dict:
    """Validate the publication portion of a .realmat/book.json file."""

    config = _require_mapping(config, "config")
    stage = _validate_stage(config.get("translation_stage"))
    entrypoint = _validate_id(config.get("entrypoint"), "entrypoint")
    publications = _validate_publications(
        config.get("publications"),
        require_pdf_url=False,
    )
    pdf_publications = [publication for publication in publications if publication["id"] == "pdf"]
    if len(pdf_publications) != 1:
        raise ContractError("A configuração deve conter exatamente uma publicação PDF canônica.")

    by_id = {publication["id"]: publication for publication in publications}
    if entrypoint not in by_id:
        raise ContractError("entrypoint deve apontar para uma publicação configurada.")
    if stage not in STAGES:  # pragma: no cover - _validate_stage already enforces this.
        raise ContractError("translation_stage inválido.")
    return config


def _release_pdf_url(repository: str, tag: str, pdf_name: str) -> str:
    return f"https://github.com/{repository}/releases/download/{tag}/{pdf_name}"


def resolve_manifest(
    config: object,
    *,
    repository: str,
    tag: str,
    pdf_name: str,
) -> dict:
    """Resolve configured publications into final URLs for a release."""

    config = validate_book_config(config)
    if not isinstance(repository, str) or REPOSITORY.fullmatch(repository) is None:
        raise ContractError("repository inválido.")
    if stage_for_version(tag) != config["translation_stage"]:
        raise ContractError("translation_stage incompatível com a versão da release.")
    if not isinstance(pdf_name, str) or SAFE_FILENAME.fullmatch(pdf_name) is None:
        raise ContractError("pdf_name inválido.")

    publications: list[dict] = []
    for publication_value in config["publications"]:
        publication = _require_mapping(publication_value, "publications item")
        publication_id = publication["id"]
        resolved = {
            "id": publication_id,
            "label": publication["label"],
        }
        if publication.get("format") is not None:
            resolved["format"] = publication["format"]
        if publication_id == "pdf":
            resolved["url"] = _release_pdf_url(repository, tag, pdf_name)
        else:
            resolved["url"] = publication["url"]
        publications.append(resolved)

    entrypoint_id = config["entrypoint"]
    entrypoint_publication = next(
        publication for publication in publications if publication["id"] == entrypoint_id
    )
    manifest = {
        "translation_stage": config["translation_stage"],
        "entrypoint": {
            "id": entrypoint_publication["id"],
            "label": entrypoint_publication["label"],
            "url": entrypoint_publication["url"],
        },
        "publications": publications,
    }
    validate_publication_manifest(manifest)
    return manifest


def _load_config(path: str) -> dict:
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ContractError(f"Não foi possível ler a configuração: {error}") from error


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True, help="caminho para .realmat/book.json")
    parser.add_argument("--repository")
    parser.add_argument("--tag")
    parser.add_argument("--pdf-name")
    parser.add_argument("--version", help="versão a conferir contra translation_stage")
    parser.add_argument("--output", help="arquivo JSON para um manifesto resolvido")
    parser.add_argument("--json", action="store_true", help="imprime apenas o JSON resolvido")
    args = parser.parse_args(argv)

    try:
        config = _load_config(args.config)
        validate_book_config(config)
        if args.version is not None and stage_for_version(args.version) != config["translation_stage"]:
            raise ContractError("translation_stage incompatível com a versão informada.")

        resolve_args = (args.repository, args.tag, args.pdf_name)
        if any(value is not None for value in resolve_args):
            if not all(value is not None for value in resolve_args):
                raise ContractError("repository, tag e pdf-name devem ser informados juntos.")
            manifest = resolve_manifest(
                config,
                repository=args.repository,
                tag=args.tag,
                pdf_name=args.pdf_name,
            )
            rendered = json.dumps(manifest, ensure_ascii=False, indent=2) + "\n"
            if args.output:
                Path(args.output).write_text(rendered, encoding="utf-8")
            elif args.json:
                print(json.dumps(manifest, ensure_ascii=False, separators=(",", ":")))
        elif args.output or args.json:
            raise ContractError("--output e --json exigem um manifesto resolvido.")

        if not args.json:
            print("publication contract verification passed")
        return 0
    except ContractError as error:
        print(f"publication contract error: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
