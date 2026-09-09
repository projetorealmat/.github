#!/usr/bin/env python3
"""Static contract tests for the reusable PreTeXt backend."""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = (
    ROOT / ".github/workflows/book-ci.yml",
    ROOT / ".github/workflows/book-publish-release.yml",
)
BUILD_SCRIPT = ROOT / "scripts/build-book.sh"


def require(text: str, fragment: str, source: Path) -> None:
    assert fragment in text, f"{fragment!r} não encontrado em {source}"


def main() -> None:
    build = BUILD_SCRIPT.read_text(encoding="utf-8")
    require(build, "PRETEXT_GENERATE", BUILD_SCRIPT)
    require(build, "PRETEXT_CACHED_ASSETS_SOURCE", BUILD_SCRIPT)
    require(build, "PRETEXT_CACHED_ASSETS_DESTINATION", BUILD_SCRIPT)
    require(build, "--no-generate", BUILD_SCRIPT)
    require(build, 'cp -a "${PRETEXT_CACHED_ASSETS_SOURCE}/."', BUILD_SCRIPT)

    for workflow in WORKFLOWS:
        text = workflow.read_text(encoding="utf-8")
        require(text, '"lxml<6.1.3"', workflow)
        require(text, '"pretext_generate"', workflow)
        require(text, '"pretext_cached_assets_source"', workflow)
        require(text, '"pretext_cached_assets_destination"', workflow)
        require(text, "PRETEXT_GENERATE:", workflow)
        require(text, "PRETEXT_CACHED_ASSETS_SOURCE:", workflow)
        require(text, "PRETEXT_CACHED_ASSETS_DESTINATION:", workflow)


if __name__ == "__main__":
    main()
