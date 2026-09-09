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
assert "expected_pdf_path" in reusable_text and "sha256" in reusable_text, "catalog payload must be validated"
assert "dispatches" in reusable_text, "book publication must dispatch through the App token"

for path in WORKFLOWS:
    if path.name in REUSABLE:
        assert "workflow_call:" in path.read_text(encoding="utf-8"), (
            f"central workflow must be reusable: {path.name}"
        )

print("architecture verification passed")
