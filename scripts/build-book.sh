#!/usr/bin/env bash
set -euo pipefail

: "${BUILD_SYSTEM:?BUILD_SYSTEM is required}"
: "${PDF_NAME:?PDF_NAME is required}"

if [[ "${BUILD_SYSTEM}" == "pretext" ]]; then
  : "${PRETEXT_PROJECT_FILE:?PRETEXT_PROJECT_FILE is required}"
  : "${PRETEXT_PDF_TARGET:?PRETEXT_PDF_TARGET is required}"
  pretext build "${PRETEXT_PDF_TARGET}"
  if [[ -n "${PRETEXT_WEB_TARGET:-}" ]]; then
    pretext build "${PRETEXT_WEB_TARGET}"
    web_path="$(dirname "${PRETEXT_PROJECT_FILE}")/output/${PRETEXT_WEB_TARGET}"
    test -d "${web_path}" || { echo "Saída web PreTeXt não encontrada: ${web_path}"; exit 1; }
  fi
  pdf_path="$(dirname "${PRETEXT_PROJECT_FILE}")/output/${PRETEXT_PDF_TARGET}/main.pdf"
  test -f "${pdf_path}" || { echo "PDF PreTeXt não encontrado: ${pdf_path}"; exit 1; }
  cp "${pdf_path}" "${PDF_NAME}"
elif [[ "${BUILD_SYSTEM}" == "latex" ]]; then
  : "${LATEX_ENTRYPOINT:?LATEX_ENTRYPOINT is required}"
  engine="${LATEX_ENGINE:-xelatex}"
  case "${engine}" in
    pdflatex) latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error "${LATEX_ENTRYPOINT}" ;;
    xelatex) latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error "${LATEX_ENTRYPOINT}" ;;
    lualatex) latexmk -lualatex -interaction=nonstopmode -halt-on-error -file-line-error "${LATEX_ENTRYPOINT}" ;;
    *) echo "latex_engine inválido: ${engine}"; exit 1 ;;
  esac
  base="${LATEX_ENTRYPOINT%.tex}"
  if [[ -f "${base}.idx" ]]; then makeindex "${base}"; fi
  if [[ -f "${base}.glo" ]]; then makeglossaries "${base}"; fi
  case "${engine}" in
    pdflatex) latexmk -pdf -interaction=nonstopmode -halt-on-error -file-line-error "${LATEX_ENTRYPOINT}" ;;
    xelatex) latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error "${LATEX_ENTRYPOINT}" ;;
    lualatex) latexmk -lualatex -interaction=nonstopmode -halt-on-error -file-line-error "${LATEX_ENTRYPOINT}" ;;
  esac
  pdf_path="${base}.pdf"
  test -f "${pdf_path}" || { echo "PDF LaTeX não encontrado: ${pdf_path}"; exit 1; }
  cp "${pdf_path}" "${PDF_NAME}"
else
  echo "BUILD_SYSTEM inválido: ${BUILD_SYSTEM}"
  exit 1
fi

test -s "${PDF_NAME}"
