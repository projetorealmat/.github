#!/usr/bin/env bash
set -euo pipefail

: "${BUILD_SYSTEM:?BUILD_SYSTEM is required}"
: "${PDF_NAME:?PDF_NAME is required}"

if [[ "${BUILD_SYSTEM}" == "pretext" ]]; then
  : "${PRETEXT_PROJECT_FILE:?PRETEXT_PROJECT_FILE is required}"
  : "${PRETEXT_PDF_TARGET:?PRETEXT_PDF_TARGET is required}"
  pretext_build_options=()
  case "${PRETEXT_GENERATE:-true}" in
    true) ;;
    false) pretext_build_options+=(--no-generate) ;;
    *) echo "PRETEXT_GENERATE inválido: ${PRETEXT_GENERATE}"; exit 1 ;;
  esac

  if [[ -n "${PRETEXT_CACHED_ASSETS_SOURCE:-}" ]]; then
    cached_destination="${PRETEXT_CACHED_ASSETS_DESTINATION:-generated-assets}"
    case "${cached_destination}" in
      /*|..|../*|*/../*|*/..) echo "Destino de assets PreTeXt inválido: ${cached_destination}"; exit 1 ;;
    esac
    test -d "${PRETEXT_CACHED_ASSETS_SOURCE}" || {
      echo "Assets PreTeXt não encontrados: ${PRETEXT_CACHED_ASSETS_SOURCE}"
      exit 1
    }
    mkdir -p "${cached_destination}"
    cp -a "${PRETEXT_CACHED_ASSETS_SOURCE}/." "${cached_destination}/"
  fi

  pretext build "${PRETEXT_PDF_TARGET}" "${pretext_build_options[@]}"
  if [[ -n "${PRETEXT_WEB_TARGET:-}" ]]; then
    pretext build "${PRETEXT_WEB_TARGET}" "${pretext_build_options[@]}"
    web_path="$(dirname "${PRETEXT_PROJECT_FILE}")/output/${PRETEXT_WEB_TARGET}"
    test -d "${web_path}" || { echo "Saída web PreTeXt não encontrada: ${web_path}"; exit 1; }
    test -s "${web_path}/index.html" || { echo "Página inicial PreTeXt não encontrada: ${web_path}/index.html"; exit 1; }
  fi
  pdf_output_dir="$(dirname "${PRETEXT_PROJECT_FILE}")/output/${PRETEXT_PDF_TARGET}"
  pdf_path="${pdf_output_dir}/$(basename "${PDF_NAME}")"
  if [[ ! -f "${pdf_path}" ]]; then
    shopt -s nullglob
    pretext_pdfs=("${pdf_output_dir}"/*.pdf)
    shopt -u nullglob
    if (( ${#pretext_pdfs[@]} != 1 )); then
      echo "PDF PreTeXt não encontrado de forma inequívoca em: ${pdf_output_dir}"
      exit 1
    fi
    pdf_path="${pretext_pdfs[0]}"
  fi
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
