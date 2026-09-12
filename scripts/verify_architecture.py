#!/usr/bin/env python3
"""Static checks for the REALMat centralized workflow contract."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
REUSABLE = {
    "book-ci.yml",
    "book-prepare-release.yml",
    "book-publish-release.yml",
    "portal-catalog-sync.yml",
}
assert WORKFLOWS, "no central workflows found"
assert REUSABLE.issubset({path.name for path in WORKFLOWS}), "central workflow is missing"
assert (ROOT / ".github/workflows/ci.yml").exists(), "central CI workflow is missing"
assert (ROOT / "scripts/publication_contract.py").exists(), "publication contract script is missing"

reusable_text = "\n".join(
    path.read_text(encoding="utf-8")
    for path in WORKFLOWS
    if path.name in REUSABLE
)
all_text = "\n".join(path.read_text(encoding="utf-8") for path in WORKFLOWS)

for legacy_name in ("REALMAT_AUTOMATION_TOKEN", "PORTAL_DISPATCH_TOKEN"):
    assert legacy_name not in all_text, f"legacy credential remains: {legacy_name}"

assert "actions/create-github-app-token@" in reusable_text, "App token action is required"
assert "REALMAT_AUTOMATION_APP_ID" in reusable_text, "App ID variable is required"
assert "REALMAT_AUTOMATION_PRIVATE_KEY" in reusable_text, "App private key secret is required"
assert "gh pr merge" in reusable_text and "--auto" in reusable_text, "catalog PR must request auto-merge"
assert "--squash" in reusable_text, "catalog auto-merge method must be explicit"
assert "client_payload" in reusable_text, "catalog workflow must consume the dispatch payload"
assert "translation_stage" in reusable_text, "catalog payload must carry translation stage"
assert "entrypoint" in reusable_text and "publications" in reusable_text, "catalog payload must carry generic publications"
assert "publication_contract.py" in reusable_text, "reusable workflows must use the central publication contract"
assert "expected_pdf_path" not in reusable_text, "legacy PDF-only catalog path remains"
assert "dispatches" in reusable_text, "book publication must dispatch through the App token"

for path in WORKFLOWS:
    if path.name in REUSABLE:
        assert "workflow_call:" in path.read_text(encoding="utf-8"), (
            f"central workflow must be reusable: {path.name}"
        )

print("architecture verification passed")
