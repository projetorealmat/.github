#!/usr/bin/env python3
"""Static checks for the REALMat centralized workflow contract."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = sorted((ROOT / ".github" / "workflows").glob("*.yml"))
assert WORKFLOWS, "no reusable workflows found"
text = "\n".join(path.read_text(encoding="utf-8") for path in WORKFLOWS)

for legacy_name in ("REALMAT_AUTOMATION_TOKEN", "PORTAL_DISPATCH_TOKEN"):
    assert legacy_name not in text, f"legacy credential remains: {legacy_name}"

assert "actions/create-github-app-token@" in text, "App token action is required"
assert "REALMAT_AUTOMATION_APP_ID" in text, "App ID variable is required"
assert "REALMAT_AUTOMATION_PRIVATE_KEY" in text, "App private key secret is required"
assert "gh pr merge" in text and "--auto" in text, "catalog PR must request auto-merge"
assert "--squash" in text, "catalog auto-merge method must be explicit"
assert "client_payload" in text, "catalog workflow must consume the dispatch payload"
assert any(path.name == "portal-catalog-sync.yml" for path in WORKFLOWS), (
    "catalog workflow must have a stable central name"
)
assert "expected_pdf_path" in text and "sha256" in text, "catalog payload must be validated"
assert 'gh api --method POST "repos/${PORTAL_REPOSITORY}/dispatches"' in text, (
    "book publication must dispatch through the App token"
)

for path in WORKFLOWS:
    assert "workflow_call:" in path.read_text(encoding="utf-8"), (
        f"central workflow must be reusable: {path.name}"
    )

print("architecture verification passed")
