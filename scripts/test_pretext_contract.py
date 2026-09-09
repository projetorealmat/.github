#!/usr/bin/env python3
"""Static contract tests for the reusable REALMat build backend."""

import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory


ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = (
    ROOT / ".github/workflows/book-ci.yml",
    ROOT / ".github/workflows/book-publish-release.yml",
)
BUILD_SCRIPT = ROOT / "scripts/build-book.sh"


def require(text: str, fragment: str, source: Path) -> None:
    assert fragment in text, f"{fragment!r} não encontrado em {source}"


def test_pretext_build_accepts_document_named_pdf() -> None:
    """PreTeXt may emit the source document name instead of main.pdf."""
    with TemporaryDirectory() as temporary:
        root = Path(temporary)
        fake_bin = root / "bin"
        fake_bin.mkdir()
        fake_pretext = fake_bin / "pretext"
        fake_pretext.write_text(
            """#!/usr/bin/env bash
set -euo pipefail
[[ "$1" == "build" ]]
case "$2" in
  print)
    mkdir -p output/print
    printf 'fake pdf' > output/print/aata.pdf
    ;;
  web)
    mkdir -p output/web
    printf '<!doctype html>' > output/web/index.html
    ;;
esac
""",
            encoding="utf-8",
        )
        fake_pretext.chmod(0o755)
        environment = os.environ.copy()
        environment.update(
            {
                "BUILD_SYSTEM": "pretext",
                "PDF_NAME": "aata.pdf",
                "PRETEXT_PROJECT_FILE": "project.ptx",
                "PRETEXT_PDF_TARGET": "print",
                "PRETEXT_WEB_TARGET": "web",
                "PATH": f"{fake_bin}:{environment['PATH']}",
            }
        )
        result = subprocess.run(
            ["bash", str(BUILD_SCRIPT)],
            cwd=root,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0, result.stdout + result.stderr
        assert (root / "aata.pdf").read_bytes() == b"fake pdf"


def test_shared_toolchain_is_complete() -> None:
    """The central workflow owns the complete LaTeX toolchain."""
    for workflow in WORKFLOWS:
        text = workflow.read_text(encoding="utf-8")
        require(text, "texlive-full", workflow)


def main() -> None:
    build = BUILD_SCRIPT.read_text(encoding="utf-8")
    require(build, "PRETEXT_GENERATE", BUILD_SCRIPT)
    require(build, "PRETEXT_CACHED_ASSETS_SOURCE", BUILD_SCRIPT)
    require(build, "PRETEXT_CACHED_ASSETS_DESTINATION", BUILD_SCRIPT)
    require(build, "--no-generate", BUILD_SCRIPT)
    require(build, "cp -a ", BUILD_SCRIPT)

    for workflow in WORKFLOWS:
        text = workflow.read_text(encoding="utf-8")
        require(text, '"lxml<6.1.3"', workflow)
        require(text, '"pretext_generate"', workflow)
        require(text, '"pretext_cached_assets_source"', workflow)
        require(text, '"pretext_cached_assets_destination"', workflow)
        require(text, "PRETEXT_GENERATE:", workflow)
        require(text, "PRETEXT_CACHED_ASSETS_SOURCE:", workflow)
        require(text, "PRETEXT_CACHED_ASSETS_DESTINATION:", workflow)

    test_pretext_build_accepts_document_named_pdf()
    test_shared_toolchain_is_complete()


if __name__ == "__main__":
    main()
