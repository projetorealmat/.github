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

- book-ci.yml: compila e valida o backend declarado pelo livro;
- book-prepare-release.yml: abre a Release PR com a versão e a data;
- book-publish-release.yml: depois do merge da Release PR, cria tag, GitHub Release, PDF, fontes e SHA256;
- portal-catalog-sync.yml: valida o evento e abre a PR do catálogo, solicitando auto-merge.

A manutenção desta biblioteca é verificada pelo ci.yml. Os repositórios consumidores devem chamar os workflows por uma referência estável, @v2, criada depois que esta versão for revisada e mesclada.

## Contrato de um livro

Cada repositório projetorealmat/<livro> é a edição REALMat traduzida/adaptada que o projeto distribui. A origem externa aparece apenas como proveniência, créditos e licença; ela não é um item separado do catálogo.

O repositório mantém:

- conteúdo-fonte e arquivos específicos da edição;
- .realmat/book.json, com metadados, backend e entrada principal;
- CITATION.cff;
- marcadores de release no README.md;
- callers finos para verificação, preparação e publicação.

O backend pode ser latex ou pretext. O workflow central não força a conversão de um livro para outro formato de entrada. Em PreTeXt, a saída web pode ser compilada como verificação; a publicação de novos formatos no catálogo deve ser adicionada ao contrato de artefatos quando houver uma edição pronta para isso.

Uma validação editorial específica pode ser mantida no próprio livro quando realmente depender do seu conteúdo; ela não deve duplicar o build central.

## Fluxo

1. PRs normais alteram o conteúdo da edição e passam pelo check de compilação.
2. O usuário aciona Preparar release PR.
3. O usuário revisa e mescla a Release PR.
4. A automação publica a tag, a GitHub Release, o PDF, as fontes e os checksums.
5. A automação envia a atualização ao portal.
6. O portal valida catálogo, links, assets e Pages; somente então a PR do catálogo pode fazer auto-merge e o site pode ser publicado.

Apenas a Release PR é uma decisão editorial humana. A atualização do catálogo é mecânica, mas continua subordinada aos checks obrigatórios do portal.
