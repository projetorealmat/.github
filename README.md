# REALMat — automação comum

Este repositório é a biblioteca central de automação do REALMat. Ele não contém o texto dos livros: mantém os workflows reutilizáveis, os scripts de verificação e o contrato comum para as edições traduzidas e adaptadas.

O repositório pode ser público porque workflows e scripts não são segredos. A chave privada da GitHub App fica exclusivamente nos secrets da organização e nunca deve aparecer aqui.

## Configuração administrativa única

A organização usa a GitHub App REALMat Automation, instalada nos repositórios do REALMat, com:

- variável organizacional REALMAT_AUTOMATION_APP_ID;
- secret organizacional REALMAT_AUTOMATION_PRIVATE_KEY;
- permissões mínimas para conteúdo e pull requests nos repositórios necessários.

Não há PAT por livro, REALMAT_AUTOMATION_TOKEN ou PORTAL_DISPATCH_TOKEN.

## Workflows centrais

Os quatro workflows reutilizáveis são:

- book-ci.yml: valida o contrato e compila o PDF do backend declarado pelo livro;
- book-prepare-release.yml: abre a Release PR, atualiza a versão e lista as publicações no README;
- book-publish-release.yml: depois do merge da Release PR, cria a tag, a GitHub Release, o PDF, as fontes, os checksums e o manifesto de publicações;
- portal-catalog-sync.yml: valida o evento e abre a PR do catálogo, solicitando auto-merge.

A manutenção desta biblioteca é verificada pelo ci.yml. Os consumidores novos devem chamar os workflows por uma referência estável @v3. A referência @v2 permanece imutável para consumidores legados.

## Contrato de um livro

Cada repositório projetorealmat/<livro> é a edição REALMat traduzida/adaptada que o projeto distribui. A origem externa aparece apenas como proveniência, créditos e licença; ela não é um item separado do catálogo.

O repositório mantém:

- conteúdo-fonte e arquivos específicos da edição;
- .realmat/book.json, com metadados, backend e publicações;
- CITATION.cff;
- marcadores de release e links de publicação no README.md;
- callers finos para verificação, preparação e publicação.

O backend pode ser latex ou pretext. O workflow central compila e verifica o PDF canônico. Formatos adicionais são preparados pela própria edição e entram no manifesto como URLs finais; o portal não os compila nem os espelha.

Um exemplo mínimo de configuração é:

~~~json
{
  "translation_stage": "unreviewed",
  "entrypoint": "pdf",
  "publications": [
    {
      "id": "pdf",
      "label": "PDF",
      "format": "pdf"
    }
  ]
}
~~~

O url do PDF pode ser omitido em .realmat/book.json: o workflow o resolve para o asset PDF da GitHub Release. Publicações não-PDF devem informar sua URL final. Quando uma edição oferecer HTML, por exemplo:

~~~json
{
  "translation_stage": "reviewed",
  "entrypoint": "html",
  "publications": [
    {
      "id": "html",
      "label": "Ler no navegador",
      "format": "html",
      "url": "https://exemplo.org/livro/"
    },
    {
      "id": "pdf",
      "label": "PDF",
      "format": "pdf"
    },
    {
      "id": "epub",
      "label": "EPUB",
      "format": "epub",
      "url": "https://exemplo.org/livro/livro.epub"
    }
  ]
}
~~~

A publicação id: "pdf" é obrigatória. O entrypoint deve apontar para uma publicação declarada. O contrato preserva a lista completa de publicações, mas a interface do portal usa somente a entrada principal, o PDF e o repositório.

## Nível da tradução

O nível é validado pelo primeiro componente da versão:

| Versão | Código | Rótulo |
|---|---|---|
| v0.x.x | unreviewed | Tradução não revisada |
| v1.x.x | reviewed | Tradução revisada |
| v2.x.x ou maior | adapted | Tradução revisada e adaptada |

O rótulo é responsabilidade do portal; o livro informa apenas o código no contrato.

## Fluxo

1. PRs normais alteram o conteúdo da edição e passam pelo check de compilação.
2. O usuário aciona Preparar release PR.
3. A automação atualiza CITATION.cff e a seção de publicações do README.
4. O usuário revisa e mescla a Release PR.
5. A automação publica a tag, a GitHub Release, o PDF, as fontes, os checksums e o manifesto.
6. A automação envia a atualização ao portal.
7. O portal valida catálogo, links e Pages; somente então a PR do catálogo pode fazer auto-merge.

A Release PR é a decisão editorial humana. A atualização do catálogo é mecânica, mas continua subordinada aos checks obrigatórios do portal.

## Compatibilidade

@v2 não deve ser atualizado nem excluído. @v3 é o contrato para os consumidores migrados e deve receber a proteção administrativa contra atualização e exclusão assim que for publicado.

A migração converte os registros existentes do catálogo para entrypoint, publications e translation_stage sem alterar as releases já publicadas. Recursos particulares de uma obra, como scripts, variantes e documentação técnica, permanecem no repositório dessa obra.
