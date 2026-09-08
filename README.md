# REALMat — automação comum

Este repositório contém os workflows reutilizáveis usados pelos livros e pelo portal do REALMat.

## Configuração administrativa única

Crie a GitHub App organizacional `REALMat Automation`, instale-a nos repositórios do REALMat e configure:

- variável organizacional `REALMAT_AUTOMATION_APP_ID`;
- secret organizacional `REALMAT_AUTOMATION_PRIVATE_KEY`;
- permissões da App: `Contents: Read and write`, `Pull requests: Read and write` e `Metadata: Read-only`.

A chave privada não pertence a este repositório e não deve aparecer em commits, logs ou mensagens.

O repositório do portal também precisa permitir auto-merge, e sua branch `main` deve exigir os checks do build do Pages e dos links externos. Os repositórios de livros devem exigir seus checks de PDF e links.

## Uso por um livro

O livro mantém um arquivo `.realmat/book.json` com seus metadados e seus workflows chamam:

```yaml
jobs:
  prepare:
    uses: projetorealmat/.github/.github/workflows/book-prepare-release.yml@v1
    with:
      config: .realmat/book.json
      version: ${{ inputs.version }}
      release_date: ${{ inputs.release_date }}
    secrets: inherit
```

O workflow de publicação usa `book-publish-release.yml@v1`. A referência `v1` deve ser criada neste repositório somente depois da validação do conjunto inicial.

## Uso pelo portal

O portal chama `portal-catalog-sync.yml@v1` a partir de um wrapper `repository_dispatch`. O workflow valida o payload, atualiza o catálogo, abre a PR com a identidade da App e solicita auto-merge. Não há PAT por livro e não há `PORTAL_DISPATCH_TOKEN`.
