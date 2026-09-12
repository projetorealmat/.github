# Contrato de entrada e publicações por links

- **Status:** proposta revisada para aprovação
- **Data:** 2026-09-12
- **Escopo:** projetorealmat/.github, repositórios de livros REALMat e portal projetorealmat/projetorealmat.github.io

## Decisão

A listagem geral do REALMat continuará apresentando os livros como itens do catálogo. Os dois botões não ficam nessa listagem.

Ao abrir a página individual de um livro, por exemplo /livros/forallx/, serão exibidas somente duas ações:

1. **Ler o livro** — abre a publicação principal;
2. **Repositório** — abre o repositório da edição e dá acesso a fontes, arquivos editáveis, documentação e demais recursos.

A publicação principal funciona como ponto de entrada para os outros formatos:

- se a edição oferece somente PDF, o botão **Ler o livro** abre o PDF diretamente no navegador; o visualizador de PDF oferece sua própria opção de download;
- se a edição oferece HTML, o botão **Ler o livro** abre o HTML;
- o HTML deve conter um menu ou seção de navegação com os demais formatos publicados, incluindo PDF, EPUB, versões acessíveis, arquivos para impressão e outros;
- se uma edição tiver vários formatos, mas não tiver HTML, deverá oferecer uma página de entrada equivalente, mantida pela própria edição, que reúna os links para esses formatos.

O README do repositório deve listar todos os links de todos os formatos. A lista completa fica disponível para quem consulta o repositório, mas não será reproduzida como vários botões na listagem do catálogo nem na página individual do livro.

## Contexto

As edições atuais demonstram por que o contrato precisa ser genérico:

- projetorealmat/forallx usa forallx.tex, XeLaTeX e atualmente publica PDF;
- projetorealmat/forallx-yyc usa forallxyyc.tex, pdfLaTeX e possui estrutura BookML para possíveis variantes de PDF, HTML e SCORM.

O portal não deve impor BookML, PreTeXt, LaTeX, um diretório de saída ou qualquer outra estrutura interna. Cada edição prepara os formatos que realmente oferece e informa os links finais dessas publicações.

## Objetivos

1. Manter a página de cada livro visualmente simples.
2. Permitir que cada livro ofereça os formatos que realmente possui.
3. Usar uma publicação principal como ponto de entrada.
4. Manter todos os links disponíveis no README da edição.
5. Fazer com que HTML, PDF, EPUB e outros formatos possam coexistir sem alterações específicas no código do portal.
6. Dar acesso aos arquivos editáveis por meio de um único link para o repositório.
7. Evitar que recursos particulares de uma obra sejam centralizados em .github.
8. Preservar as releases e o catálogo existentes durante a migração.

## Fora do escopo

- Criar uma lista de botões de formatos na listagem ou na página individual do livro.
- Fazer o portal compilar HTML, PDF, EPUB, BookML, PreTeXt ou SCORM.
- Fazer o portal descobrir formatos lendo texto livre do README.
- Copiar obrigatoriamente todos os formatos para o Pages.
- Inventar links para formatos ainda não publicados.
- Alterar a tag @v2 do repositório central.
- Exigir que todos os livros ofereçam PDF ou HTML.

## Contrato da publicação

O contrato comum será um payload de links finais entregue pela edição ao fluxo de publicação. Ele não presume como os arquivos foram produzidos.

Exemplo para uma edição que oferece somente PDF:

~~~json
{
  "entrypoint": "pdf",
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
  "entrypoint": "html",
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

- entrypoint é obrigatório e deve corresponder exatamente ao id de uma publicação.
- publications deve conter todos os formatos publicados para aquela versão.
- Cada publicação deve ter id, label e url.
- format é opcional e apenas descritivo; formatos novos não devem quebrar o portal.
- As URLs devem ser finais, válidas e acessíveis. O contrato comum não exige o uso de assets nem que o portal faça espelhamento.
- A URL do entrypoint deve abrir efetivamente a leitura ou a página de entrada da edição.
- Quando o entrypoint for PDF, a URL deve permitir sua abertura no navegador, para que o usuário disponha do visualizador e da opção de download.
- Quando houver HTML, ele será o entrypoint preferencial e deverá oferecer navegação para todas as demais publicações declaradas.
- Se houver vários formatos sem HTML, a edição deverá fornecer uma página de entrada equivalente, com links para todos eles.
- A ordem de publications será preservada no README e nos dados da release, mas não será transformada em botões na listagem ou na página individual do livro.
- A lista completa pode conter links para releases, sites externos, leitores HTML ou outros serviços mantidos pela edição.
- O contrato não terá um campo source dentro de publications. A origem do livro é metadado editorial separado.

## Catálogo, listagem e página individual

O catálogo armazenará o entrypoint, a lista completa de publicações e o repositório da edição.

~~~json
{
  "version": "v0.1.0",
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

Na página individual do livro, por exemplo /livros/forallx/, serão exibidos somente:

- **Ler o livro** → URL do entrypoint;
- **Repositório** → URL do repositório da edição, derivada do campo repository.

Não haverá um botão separado para download, release, PDF, EPUB ou qualquer outro formato. O download deverá ocorrer pelo visualizador do PDF ou pelo menu da publicação principal.

A lista publications será mantida nos dados para validação, sincronização, histórico e uso pelo README ou pelas publicações, mas não será apresentada como uma coleção de botões na página individual.

O portal não deve mostrar botões vazios, não deve escolher um formato por heurística própria e não deve substituir o entrypoint informado pela edição.

O link para a fonte original pode aparecer em créditos ou metadados editoriais, mas não substitui o botão **Repositório**, que deve apontar para a edição REALMat.

## Responsabilidades da edição

Cada repositório de livro:

- prepara e publica os formatos que realmente oferece;
- define qual publicação é o entrypoint;
- garante que o entrypoint permita chegar aos demais formatos;
- mantém no README uma seção com todos os links das publicações;
- mantém a explicação específica de compilação, variantes e particularidades da obra;
- mantém fontes, arquivos editáveis, scripts e documentação no próprio repositório;
- preserva origem, créditos e licença.

O README deve conter, no mínimo:

1. identificação e descrição curta da edição;
2. versão recomendada;
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

Em uma edição que só oferece PDF:

~~~markdown
## Publicação

- [Abrir o PDF no navegador](https://exemplo.org/livro/v0.1.0/livro.pdf)

O visualizador do navegador oferece a opção de download.
~~~

## Responsabilidades do .github central

O repositório central:

- define e valida o payload genérico;
- transporta entrypoint e publications para o portal;
- valida URLs, ids, duplicações e a existência do entrypoint;
- mantém compatibilidade durante a migração;
- não precisa conhecer BookML, PreTeXt, drivers LaTeX ou scripts de uma obra;
- não transforma a lista em uma interface cheia de botões;
- não decide qual formato deve ser o entrypoint de um livro.

A edição ou seu workflow específico deve produzir os links finais. O contrato comum começa nesses links finais, e não na estrutura interna usada para gerar os arquivos.

A implementação deve ser publicada como uma nova versão do contrato central. A referência @v2 e seu comportamento permanecerão intactos até a nova versão estar verificada.

## Responsabilidades do portal

O portal:

- apresenta os livros na listagem geral;
- gera ou exibe a página individual de cada livro;
- mantém nessa página somente as ações **Ler o livro** e **Repositório**;
- valida os dados recebidos;
- preserva a lista completa no catálogo;
- não compila livros;
- não interpreta READMEs;
- não exige PDF, HTML ou EPUB quando não forem declarados;
- não espelha automaticamente todos os formatos;
- pode manter a distribuição local de um PDF legado durante a migração, desde que isso não crie botões adicionais nem altere o modelo público.

## Migração inicial

1. Manter o catálogo atual funcionando para forallx e forallx-yyc.
2. Adicionar o novo contrato e o comportamento de dois botões na página individual do livro em uma nova versão central.
3. Atualizar os READMEs dos livros com todos os links realmente disponíveis.
4. Registrar forallx com PDF como entrypoint.
5. Registrar forallx-yyc com PDF como entrypoint enquanto o HTML ainda não estiver efetivamente publicado.
6. Quando o HTML do forallx-yyc estiver publicado e testado, torná-lo o entrypoint e manter no README os links para HTML, PDF e demais formatos disponíveis.
7. Fazer o portal aceitar o formato legado atual durante a transição.
8. Adicionar testes para:
   - edição somente com PDF;
   - edição com HTML, PDF e EPUB;
   - entrypoint inexistente;
   - link duplicado ou sem URL;
   - formato desconhecido;
   - vários formatos sem HTML;
   - README contendo todos os links declarados;
   - repositório de edição separado da fonte original.

## Critério de aceitação

A arquitetura estará correta quando:

- a página individual de cada livro tiver somente os botões **Ler o livro** e **Repositório**;
- um livro somente com PDF abrir o PDF no navegador;
- um livro com HTML abrir o HTML, cujo menu conduza aos demais formatos;
- todos os links de formato estiverem disponíveis no README da edição;
- os arquivos editáveis forem acessíveis pelo botão **Repositório**;
- o portal não exigir ou inventar formatos;
- um terceiro livro puder declarar outro conjunto de publicações sem alteração específica no portal;
- nenhum recurso particular de um livro precisar ser colocado no .github central;
- as releases e links antigos continuarem válidos;
- todos os checks do central, dos livros e do portal permanecerem verdes.
