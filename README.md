# REALMat — automação comum

Este repositório contém os workflows reutilizáveis usados pelos livros e pelo portal do REALMat.

## Configuração administrativa única

Crie a GitHub App organizacional `REALMat Automation`, instale-a nos repositórios do REALMat e configure:

- variável organizacional `REALMAT_AUTOMATION_APP_ID`;
- secret organizacional `REALMAT_AUTOMATION_PRIVATE_KEY`;
- permissões da App: `Contents: Read and write`, `Pull requests: Read and write` e `Metadata: Read-only`.

A chave privada não pertence a este repositório e não deve aparecer em commits, logs ou mensagens.

O repositório do portal também precisa permitir auto-merge, e sua branch `main` deve exigir os checks do build do Pages e dos links externos. Os repositórios de livros devem exigir o check de compilação do PDF.

## Contrato mínimo de um livro

Cada livro mantém somente `.realmat/book.json`, `CITATION.cff`, os marcadores de release no `README.md` e três callers finos em `.github/workflows/`:

- `book-ci.yml` chama `book-ci.yml` para validar o backend declarado;
- `prepare-release-pr.yml` chama `book-prepare-release.yml`;
- `release-pdf.yml` chama `book-publish-release.yml`.

O JSON declara os metadados do catálogo e uma entrada principal. O backend pode ser `latex` (`latex_entrypoint` e `latex_engine`) ou `pretext` (`pretext_project_file`, `pretext_pdf_target` e, opcionalmente, `pretext_web_target`).

Os callers usam a branch `main` deste repositório. A PR central deve ser mesclada antes das PRs dos livros; depois disso, cada livro passa a enxergar a mesma implementação.

## Fluxo de release

1. O usuário aciona `Preparar release PR` e informa a versão; a data pode ficar vazia.
2. A automação abre uma Release PR com metadados e README.
3. Depois do merge da Release PR, o workflow compila o PDF, cria a tag anotada, publica fontes, PDF e SHA256 na GitHub Release e envia o evento ao portal.
4. O portal valida o catálogo, abre sua PR e solicita auto-merge; os checks obrigatórios continuam sendo a condição para o merge e o deploy.

Não há PAT por livro nem `PORTAL_DISPATCH_TOKEN`.
