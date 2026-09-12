# Contrato de entrada e publicações por links

- **Status:** proposta revisada para aprovação — PDF obrigatório e `@v3` recomendado
- **Data:** 2026-09-12
- **Escopo:** projetorealmat/.github, repositórios de livros REALMat e portal projetorealmat/projetorealmat.github.io

## Decisão

A listagem geral do REALMat continuará apresentando os livros como itens do catálogo. Ela não exibirá botões específicos de formatos; o acesso à página individual continuará sendo o caminho para a edição.

Ao abrir a página individual de um livro, por exemplo `/livros/forallx/`, serão exibidas exatamente três ações:

1. **Ler o livro** — abre a publicação definida como `entrypoint`;
2. **Baixar PDF** — aponta para a publicação PDF oficial da edição;
3. **Repositório** — abre o repositório da edição e dá acesso a fontes, arquivos editáveis, documentação e demais recursos.

O PDF é uma publicação obrigatória de toda edição REALMat. Ele será o destino fixo do botão **Baixar PDF**, mesmo quando a publicação principal for HTML.

A publicação definida como `entrypoint` funciona como ponto de entrada para a leitura e para os demais formatos:

- se a edição oferece somente PDF, **Ler o livro** e **Baixar PDF** apontam para o mesmo PDF; o primeiro abre o arquivo para leitura no navegador e o segundo o apresenta como download;
- se a edição oferece HTML, **Ler o livro** abre o HTML;
- o HTML deve conter um menu ou seção de navegação com os demais formatos publicados, incluindo o PDF, EPUB, versões acessíveis, arquivos para impressão e outros;
- se uma edição tiver vários formatos, mas não tiver HTML, deverá oferecer uma página de entrada equivalente, mantida pela própria edição, que reúna os links para esses formatos.

O README do repositório deve listar todos os links de todos os formatos, incluindo obrigatoriamente o PDF. A lista completa fica disponível para quem consulta o repositório, mas não será reproduzida como vários botões de formato na listagem ou na página individual.

## Nível da tradução

Cada edição deverá informar o nível de tradução associado à versão atualmente apresentada no catálogo e na página individual do livro.

Os três níveis iniciais serão:

| Versão | Código | Rótulo exibido |
|---|---|---|
| v0.x.x | unreviewed | Tradução não revisada |
| v1.x.x | reviewed | Tradução revisada |
| v2.x.x | adapted | Tradução revisada e adaptada |

O nível será um metadado da edição/release, por exemplo:

~~~json
{
  "translation_stage": "reviewed"
}
~~~

Regras:

- o código será validado pelo contrato central;
- o rótulo será padronizado pelo portal, evitando que cada livro escreva uma variação;
- o nível deverá ser compatível com o primeiro componente da versão;
- v0.x.x não significa que o conteúdo esteja inutilizável; significa que a tradução ainda não passou pela revisão definida pelo REALMat;
- v1.x.x identifica uma tradução revisada, mas ainda fiel ao original;
- v2.x.x identifica uma tradução revisada que também recebeu adaptação autorizada;
- o modelo poderá receber novos níveis no futuro sem obrigar o portal a conhecer detalhes editoriais de cada livro.

A página individual e os itens da listagem poderão mostrar o rótulo junto da versão atual, por exemplo: **Tradução revisada · v1.0.0**. O nível não altera as três ações fixas nem a forma de acesso aos formatos.

## Contexto

As edições atuais demonstram por que o contrato precisa ser genérico:

- projetorealmat/forallx usa forallx.tex, XeLaTeX e atualmente publica PDF;
- projetorealmat/forallx-yyc usa forallxyyc.tex, pdfLaTeX e possui estrutura BookML para possíveis variantes de PDF, HTML e SCORM.

O portal não deve impor BookML, PreTeXt, LaTeX, um diretório de saída ou qualquer outra estrutura interna. Cada edição prepara os formatos que realmente oferece, garante a publicação do PDF canônico e informa os links finais dessas publicações.

## Objetivos

1. Manter a página de cada livro visualmente simples.
2. Garantir um PDF oficial para download em toda edição.
3. Permitir que cada livro ofereça, além do PDF, os formatos que realmente possui.
4. Usar uma publicação principal como ponto de entrada.
5. Manter todos os links disponíveis no README da edição.
6. Fazer com que HTML, PDF, EPUB e outros formatos possam coexistir sem alterações específicas no código do portal.
7. Dar acesso aos arquivos editáveis por meio de um único link para o repositório.
8. Evitar que recursos particulares de uma obra sejam centralizados em `.github`.
9. Preservar as releases e o catálogo existentes durante a migração.

## Fora do escopo

- Criar uma coleção de botões para cada formato na listagem ou na página individual do livro; a página individual terá somente as três ações fixas definidas neste contrato.
- Fazer o portal compilar HTML, PDF, EPUB, BookML, PreTeXt ou SCORM.
- Fazer o portal descobrir formatos lendo texto livre do README.
- Copiar obrigatoriamente todos os formatos para o Pages.
- Inventar links para formatos ainda não publicados.
- Escolher antecipadamente entre atualizar `@v2` ou criar uma nova tag sem antes avaliar compatibilidade.
- Exigir que todos os livros ofereçam HTML; o PDF canônico, porém, é obrigatório.

## Contrato da publicação

O contrato comum será um payload de links finais entregue pela edição ao fluxo de publicação. Ele não presume como os arquivos foram produzidos.

Exemplo para uma edição que oferece somente PDF:

~~~json
{
  "entrypoint": {
    "id": "pdf",
    "label": "PDF",
    "url": "https://exemplo.org/livro/v0.1.0/livro.pdf"
  },
  "publications": [
    {
      "id": "pdf",
      "label": "PDF",
      "format": "pdf",
      "url": "https://exemplo.org/livro/v0.1.0/livro.pdf"
    }
  ]
}
~~~

Exemplo para uma edição que oferece HTML, PDF e EPUB:

~~~json
{
  "entrypoint": {
    "id": "html",
    "label": "Ler no navegador",
    "url": "https://exemplo.org/livro/html/"
  },
  "publications": [
    {
      "id": "html",
      "label": "Ler no navegador",
      "format": "html",
      "url": "https://exemplo.org/livro/html/"
    },
    {
      "id": "pdf",
      "label": "PDF",
      "format": "pdf",
      "url": "https://exemplo.org/livro/v0.1.0/livro.pdf"
    },
    {
      "id": "epub",
      "label": "EPUB",
      "format": "epub",
      "url": "https://exemplo.org/livro/v0.1.0/livro.epub"
    }
  ]
}
~~~

### Regras

- `entrypoint` é obrigatório e deve ser um objeto com `id`, `label` e `url`.
- O `entrypoint.id` deve corresponder exatamente ao `id` de uma publicação, e sua URL deve ser a mesma URL dessa publicação.
- `publications` deve conter todos os formatos publicados para aquela versão.
- Toda edição deve conter exatamente uma publicação canônica com `id: "pdf"`, `format: "pdf"`, `label` e `url`. Essa publicação é obrigatória mesmo quando o `entrypoint` for HTML.
- Cada publicação deve ter `id`, `label` e `url`; `format` é opcional para publicações não-PDF e apenas descritivo.
- As URLs devem ser finais, válidas e acessíveis. O contrato comum não exige o uso de assets nem que o portal faça espelhamento.
- A URL do `entrypoint` deve abrir efetivamente a leitura ou a página de entrada da edição.
- A URL da publicação PDF deve permitir a abertura do arquivo no navegador e o download pelo botão **Baixar PDF**.
- Quando houver HTML, ele será o `entrypoint` preferencial e deverá oferecer navegação para todas as demais publicações declaradas.
- Se houver vários formatos sem HTML, a edição deverá fornecer uma página de entrada equivalente, com links para todos eles.
- A ordem de `publications` será preservada no README e nos dados da release, mas não será transformada em botões individuais de formato na listagem ou na página individual; a página individual terá apenas as três ações fixas.
- A lista completa pode conter links para releases, sites externos, leitores HTML ou outros serviços mantidos pela edição.
- O contrato não terá um campo `source` dentro de `publications`. A origem do livro é metadado editorial separado.

## Catálogo, listagem e página individual

O catálogo armazenará o `entrypoint`, a publicação PDF canônica, a lista completa de publicações e o repositório da edição.

~~~json
{
  "version": "v0.1.0",
  "translation_stage": "unreviewed",
  "repository": "projetorealmat/forallx-yyc",
  "entrypoint": {
    "id": "html",
    "label": "Ler o livro",
    "url": "https://exemplo.org/livro/html/"
  },
  "publications": [
    {
      "id": "html",
      "label": "Ler no navegador",
      "format": "html",
      "url": "https://exemplo.org/livro/html/"
    },
    {
      "id": "pdf",
      "label": "PDF",
      "format": "pdf",
      "url": "https://exemplo.org/livro/v0.1.0/livro.pdf"
    }
  ]
}
~~~

Na listagem geral, o portal deverá apresentar o livro como item do catálogo e permitir o acesso à sua página individual. A listagem não exibirá botões para os formatos.

Na página individual do livro, por exemplo `/livros/forallx/`, serão exibidos somente:

- **Ler o livro** → URL do `entrypoint`;
- **Baixar PDF** → URL da publicação cujo `id` é `pdf`;
- **Repositório** → URL do repositório da edição, derivada do campo `repository`.

Não haverá botões separados para HTML, EPUB, release ou outras variantes. O PDF terá o botão fixo **Baixar PDF** porque é o formato comum a todas as edições. Os demais formatos serão acessados pelo menu da publicação principal ou pelos links completos mantidos no README.

A lista `publications` será mantida nos dados para validação, sincronização, histórico e uso pelo README ou pelas publicações, mas não será apresentada como uma coleção de botões na página individual.

O portal não deve mostrar botões vazios, não deve escolher um formato por heurística própria e não deve substituir o `entrypoint` informado pela edição.

O link para a fonte original pode aparecer em créditos ou metadados editoriais, mas não substitui o botão **Repositório**, que deve apontar para a edição REALMat.

## Responsabilidades da edição

Cada repositório de livro:

- prepara e publica o PDF canônico e os demais formatos que realmente oferece;
- define qual publicação é o entrypoint;
- garante que o entrypoint permita chegar aos demais formatos;
- mantém no README uma seção com todos os links das publicações;
- mantém a explicação específica de compilação, variantes e particularidades da obra;
- mantém fontes, arquivos editáveis, scripts e documentação no próprio repositório;
- preserva origem, créditos e licença.

O README deve conter, no mínimo:

1. identificação e descrição curta da edição;
2. versão recomendada e nível da tradução;
3. seção com todos os formatos e seus links;
4. indicação do entrypoint;
5. arquivos e compilação específicos da edição;
6. origem, créditos e licença;
7. integração com o REALMat.

Exemplo de seção do README:

~~~markdown
## Publicações

- [Ler no navegador](https://exemplo.org/livro/html/)
- [PDF](https://exemplo.org/livro/v0.1.0/livro.pdf)
- [EPUB](https://exemplo.org/livro/v0.1.0/livro.epub)

O link principal para leitura é o HTML. O menu do leitor também reúne as demais versões.
~~~

Em uma edição que só oferece PDF (o caso mínimo obrigatório):

~~~markdown
## Publicação

- [Abrir o PDF no navegador](https://exemplo.org/livro/v0.1.0/livro.pdf)

O botão **Baixar PDF** aponta para o PDF oficial; o navegador ou o servidor de publicação realiza o download.
~~~

## Contribuição e edição

O menu **Contribuir** do site será o ponto de entrada para as instruções gerais de participação no REALMat. Ele deverá explicar, de forma centralizada:

- como localizar o repositório de uma edição;
- como criar fork ou branch;
- como propor alterações por pull request;
- como acompanhar os checks;
- como distinguir tradução não revisada, revisada e revisada e adaptada;
- onde encontrar as fontes e os arquivos editáveis.

A página individual do livro não repetirá esse manual. O botão **Repositório** levará diretamente ao repositório da edição, onde estarão os arquivos e as particularidades técnicas da obra. O README de cada livro poderá apontar para as instruções gerais do menu **Contribuir**, acrescentando somente orientações específicas quando necessário.

## Escopo de adaptação do projeto e do site

A demanda de implementação passa a incluir duas frentes relacionadas.

### Adaptação do projeto REALMat e do contrato central

- criar a versão `@v3` do contrato, mantendo `@v2` imutável para consumidores legados;
- transportar e validar `entrypoint` e `publications`;
- exigir e transportar a publicação PDF canônica;
- transportar e validar `translation_stage`;
- manter compatibilidade com o catálogo e as releases legadas durante a migração;
- adaptar os repositórios de livros somente onde for necessário para fornecer os metadados e os links finais;
- não centralizar BookML, PreTeXt, drivers LaTeX, scripts ou outros recursos específicos de uma edição.

### Adaptação do site

O site deverá ser adaptado porque a implementação atual assume PDF e apresenta ações adicionais na página individual. A adaptação necessária é limitada à camada de catálogo e navegação:

- aceitar os metadados de vários formatos;
- usar o `entrypoint` como destino de **Ler o livro**;
- usar a publicação PDF canônica como destino de **Baixar PDF**;
- exibir somente **Ler o livro**, **Baixar PDF** e **Repositório** na página individual;
- exibir o rótulo padronizado do nível da tradução;
- manter no README e nos dados os links completos de todos os formatos;
- preservar o menu **Contribuir** como local das instruções gerais;
- continuar aceitando edições com PDF como único formato;
- não compilar formatos no site;
- não criar botões individuais para EPUB, HTML, SCORM ou outras variantes além das três ações fixas.

Quando o `entrypoint` for HTML, o site apenas apontará para a página HTML e o botão de download apontará para o PDF; o menu dos demais formatos será responsabilidade da própria publicação. Quando o `entrypoint` for PDF, os botões de leitura e download apontarão para o mesmo arquivo.

## Versionamento do contrato central

A auditoria confirmou que o payload atual é incompatível com o novo contrato: ele exige PDF, usa campos específicos (`pdf_url`, `pdf_path` e `sha256`) e calcula o status editorial a partir da versão. Além disso, a tag `@v2` está protegida contra atualização e exclusão.

Por isso, a migração usará `@v3`:

- `@v2` permanecerá imutável para branches e edições legadas;
- `@v3` conterá o contrato genérico com publicação PDF canônica, `entrypoint`, `publications` e `translation_stage`;
- os cinco livros e o portal serão migrados coordenadamente para `@v3`;
- a tag `@v3` também deverá ser protegida contra atualização e exclusão;
- não serão mantidos dois caminhos de execução dentro dos consumidores novos;
- o catálogo atual será convertido para o novo modelo sem alterar as releases já publicadas.

Essa é a menor mudança que preserva a estabilidade da referência publicada e evita uma coexistência permanente de semânticas diferentes.

## Responsabilidades do .github central

O repositório central:

- define e valida o payload genérico, incluindo a publicação PDF canônica;
- transporta entrypoint e publications para o portal;
- valida URLs, ids, duplicações e a existência do entrypoint;
- mantém compatibilidade durante a migração;
- não precisa conhecer BookML, PreTeXt, drivers LaTeX ou scripts de uma obra;
- não transforma a lista em uma interface cheia de botões;
- não decide qual formato deve ser o entrypoint de um livro.

A edição ou seu workflow específico deve produzir os links finais. O contrato comum começa nesses links finais, e não na estrutura interna usada para gerar os arquivos.


## Responsabilidades do portal

O portal:

- apresenta os livros na listagem geral;
- gera ou exibe a página individual de cada livro;
- mantém nessa página somente as ações **Ler o livro**, **Baixar PDF** e **Repositório**;
- usa a publicação PDF canônica como destino do download;
- valida os dados recebidos, inclusive a existência do PDF obrigatório;
- preserva a lista completa no catálogo;
- não compila livros;
- não interpreta READMEs;
- não exige HTML, EPUB ou qualquer formato além do PDF canônico obrigatório;
- não espelha automaticamente todos os formatos;
- pode manter a distribuição local de um PDF legado durante a migração, desde que isso não crie botões adicionais nem altere o modelo público.

## Migração inicial

1. Manter o catálogo atual funcionando para `forallx` e `forallx-yyc`.
2. Atualizar o contrato central, criar `@v3`, protegê-la e migrar os consumidores coordenadamente.
3. Adicionar `translation_stage`, `entrypoint` e `publications` às configurações dos cinco livros.
4. Atualizar os READMEs dos livros com todos os links realmente disponíveis, incluindo o PDF obrigatório.
5. Registrar `forallx` com PDF como `entrypoint` e como publicação de download.
6. Registrar `forallx-yyc` com PDF como `entrypoint` e como publicação de download enquanto o HTML ainda não estiver efetivamente publicado.
7. Quando o HTML do `forallx-yyc` estiver publicado e testado, torná-lo o `entrypoint` e manter no README os links para HTML, PDF e demais formatos disponíveis.
8. Converter os registros atuais do catálogo para o novo modelo, preservando versões, releases, URLs e histórico.
9. Fazer o portal aceitar registros legados somente durante a conversão; o catálogo final deverá usar o contrato novo.
10. Adicionar testes para:
   - edição somente com PDF;
   - edição com HTML, PDF e EPUB;
   - ausência da publicação PDF obrigatória;
   - `entrypoint` inexistente ou inconsistente;
   - link duplicado ou sem URL;
   - formato desconhecido;
   - vários formatos sem HTML;
   - README contendo todos os links declarados;
   - repositório de edição separado da fonte original;
   - página individual com exatamente os três botões fixos.

## Critério de aceitação

A arquitetura estará correta quando:

- a página individual de cada livro tiver somente os botões **Ler o livro**, **Baixar PDF** e **Repositório**;
- uma edição somente com PDF abrir o PDF pelo botão de leitura e oferecer o mesmo arquivo pelo botão de download;
- uma edição com HTML abrir o HTML pelo botão de leitura e oferecer o PDF canônico pelo botão de download;
- o HTML, quando existir, conduzir aos demais formatos publicados;
- todos os links de formato, incluindo o PDF, estiverem disponíveis no README da edição;
- os arquivos editáveis forem acessíveis pelo botão **Repositório**;
- o portal não inventar formatos além do PDF obrigatório nem criar botões adicionais;
- um terceiro livro puder declarar outro conjunto de publicações sem alteração específica no portal;
- nenhum recurso particular de um livro precisar ser colocado no `.github` central;
- as releases e links antigos continuarem válidos;
- todos os checks do central, dos livros e do portal permanecerem verdes.
