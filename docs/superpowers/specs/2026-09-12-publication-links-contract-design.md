# Contrato de publicações por links

- **Status:** proposta para revisão
- **Data:** 2026-09-12
- **Escopo:** `projetorealmat/.github`, repositórios de livros REALMat e portal `projetorealmat/projetorealmat.github.io`

## Decisão

A fronteira comum entre um repositório de livro e o portal REALMat será uma lista de links de publicação, e não um formato de saída obrigatório.

Cada repositório continuará responsável por sua estrutura interna, sistema de compilação e formatos que realmente oferece. O portal receberá os links publicados, armazenará-os no catálogo da edição e os exibirá sem presumir que todos os livros possuam PDF, HTML, BookML, PreTeXt ou qualquer outro formato específico.

O contrato central validará a forma dos links, mas não implementará a produção dos formatos particulares de cada livro.

## Contexto

As edições atuais já demonstram a diferença que o contrato precisa absorver:

- `projetorealmat/forallx` usa `forallx.tex), XeLaTeX e atualmente publica o PDF `forallx.pdf`.
- `projetorealmat/forallx-yyc` usa `forallxyyc.tex), pdfLaTeX e também possui drivers BookML para variantes de PDF, HTML e SCORM.

A estrutura do repositório de origem não deve ser reproduzida no portal nem imposta às demais traduções. O README de cada edição precisa explicar apenas o que é comum ao REALMat e o que é particular daquela obra.

## Objetivos

1. Permitir que uma edição publique somente os formatos que possui.
2. Permitir que uma edição ofereça vários links para a mesma versão.
3. Permitir links para arquivos de release e links externos, como um leitor HTML hospedado em outro endereço.
4. Fazer o portal apresentar os links recebidos sem código específico para cada livro.
5. Manter o README curto, com uma parte padronizada e uma parte específica da obra.
6. Evitar que BookML, drivers LaTeX, PreTeXt ou outros recursos particulares sejam centralizados em `.github`.
7. Preservar o fluxo atual de releases e o catálogo existente durante a migração.

## Fora do escopo

- Tornar todos os livros compatíveis com HTML.
- Compilar BookML ou qualquer outro backend no repositório central.
- Fazer o portal descobrir formatos lendo texto livre dos READMEs.
- Copiar automaticamente para o Pages todo arquivo oferecido por uma edição.
- Alterar a tag `v2` do repositório central.
- Inventar links para formatos que ainda não foram publicados.

## Contrato da edição

O arquivo `.realmat/book.json` poderá declarar uma lista opcional `links`. Cada item representa uma publicação ou recurso oferecido pela edição.

Exemplo mínimo:

```json
{
  "links": [
    {
      "id": "pdf",
      "label": "PDF",
      "role": "download",
      "format": "pdf",
      "asset": "forallx.pdf",
      "primary": true
    }
  ]
}
```

Exemplo com formatos heterogêneos:

```json
{
  "links": [
    {
      "id": "pdf",
      "label": "PDF",
      "role": "download",
      "format": "pdf",
      "asset": "forallxyyc.pdf",
      "primary": true
    },
    {
      "id": "pdf-accessible",
      "label": "PDF acessível",
      "role": "download",
      "format": "pdf"
    },
    {
      "id": "html",
      "label": "Ler no navegador",
      "role": "read",
      "format": "html",
      "url": "https://exemplo.org/livro/html/"
    },
    {
      "id": "scorm",
      "label": "Pacote SCORM",
      "role": "download",
      "format": "scorm",
      "asset": "SCORM.forallxyyc.zip"
    }
  ]
}
```

### Regras dos itens

- `id` é obrigatório, único na edição e formado por letras minúsculas, números e hífens.
- `label` é obrigatório e é o texto mostrado no portal.
- `role` é obrigatório e usa inicialmente `read`, `download` ou `source`.
- `format` é opcional e descritivo; valores novos não quebram o portal.
- Exatamente um destino deve ser informado:
  - `asset`: nome do arquivo que o fluxo de publicação realmente anexará à release;
  - `url`: URL HTTPS direta que a edição oferece.
- `primary` é opcional; no máximo um link pode ser principal. Se nenhum for marcado, o portal usará o primeiro link na ordem declarada.
- A ordem declarada será preservada no README gerado e no portal.
- Um item declarado como `asset` sem o arquivo correspondente deve fazer a publicação falhar.
- Um item com `url` não será transformado nem redirecionado pelo portal.

O contrato não exige que exista um link com formato `pdf`. Durante a migração, os campos PDF já presentes no catálogo continuarão válidos para as edições atuais e serão tratados como uma forma legada do link principal.

## Payload da release e catálogo

O workflow central de publicação produzirá no evento `book-release` uma lista resolvida de links:

```json
{
  "id": "html",
  "label": "Ler no navegador",
  "role": "read",
  "format": "html",
  "url": "https://exemplo.org/livro/html/"
}
```

Para um `asset`, a URL será a URL imutável do arquivo na release. Para um `url`, a URL será preservada exatamente como declarada.

O catálogo armazenará essa lista dentro de cada release:

```json
{
  "version": "v0.1.0",
  "repository": "projetorealmat/forallx-yyc",
  "ref": "v0.1.0",
  "links": [
    {
      "id": "pdf",
      "label": "PDF",
      "role": "download",
      "format": "pdf",
      "url": "https://github.com/projetorealmat/forallx-yyc/releases/download/v0.1.0/forallxyyc.pdf",
      "primary": true
    }
  ]
}
```

Os campos `pdf_url`, `pdf_path` e `sha256` permanecerão durante a migração para não invalidar as releases já catalogadas. Eles não serão usados para obrigar novas edições a oferecerem formatos que não possuem.

O portal deverá:

- validar a lista de links;
- renderizar os links na ordem declarada;
- destacar o link principal;
- usar rótulos e funções genéricos;
- permitir novos valores de `format` sem alterar o código;
- não criar um botão HTML ou PDF quando o respectivo link não existir.

## Responsabilidades

### Repositório do livro

- mantém conteúdo, fontes, drivers, BookML, PreTeXt e scripts próprios;
- decide quais formatos realmente publica;
- declara os links e suas particularidades;
- mantém a explicação específica da obra no README;
- preserva origem, créditos e licença.

### `.github` central

- valida o contrato genérico;
- resolve links de assets para URLs de release;
- transporta links no evento para o portal;
- publica somente artefatos que o fluxo da edição realmente preparou;
- não conhece a estrutura interna de um livro;
- não contém drivers ou recursos específicos de BookML.

A implementação será publicada como uma nova versão do contrato central. A referência `@v2) e seu comportamento permanecerão intactos até a migração estar verificada.

### Portal

- valida e armazena os links recebidos;
- apresenta os links no catálogo e na página da edição;
- verifica somente os assets que forem explicitamente mantidos localmente;
- não compila livros;
- não interpreta READMEs;
- não exige um formato que não tenha sido declarado.

## Padrão dos READMEs

Cada README deverá conter, nesta ordem:

1. identificação e descrição curta da edição REALMat;
2. versão atualmente recomendada e bloco automático da release;
3. publicações disponíveis;
4. arquivos e compilação específicos da edição;
5. origem, créditos e licença;
6. integração com o REALMat.

A seção de publicações será curta e poderá ser atualizada a partir dos links da release. A seção específica poderá explicar, por exemplo:

- em `forallx`: compilação XeLaTeX e publicação em PDF;
- em `forallx-yyc`: variantes para acessibilidade/impressão, geração BookML, HTML com soluções e SCORM.

Detalhes completos da obra original permanecerão no README ou no repositório da fonte, por meio de links. O README REALMat não repetirá o README original nem a documentação central do fluxo.

## Migração inicial

1. Manter o catálogo atual funcionando para `forallx) e `forallx-yyc).
2. Adicionar o contrato de links ao validador central e ao validador do portal.
3. Atualizar os READMEs dos dois livros para o padrão comum, sem inventar publicações ainda inexistentes.
4. Registrar inicialmente o PDF já publicado de cada edição.
5. Quando o `forallx-yyc) publicar HTML, acessível, impressão, carta, soluções ou SCORM, acrescentar somente os links realmente disponíveis.
6. Adicionar testes para:
   - edição apenas com PDF;
   - edição com PDF, HTML e SCORM;
   - link externo de leitura;
   - release com asset ausente;
   - formato desconhecido, que deve ser aceito;
   - link duplicado ou sem destino, que deve falhar.

## Critério de aceitação

A arquitetura estará correta quando:

- o portal puder catalogar `forallx) sem criar campos HTML vazios;
- o portal puder catalogar `forallx-yyc) com vários links sem alteração específica no código;
- um terceiro livro puder declarar outro conjunto de links;
- o README de cada livro permanecer curto e compreensível;
- nenhum recurso específico de um livro precisar ser colocado no `.github) central;
- releases e links antigos continuarem válidos;
- todos os checks do central, dos livros e do portal permanecerem verdes.
