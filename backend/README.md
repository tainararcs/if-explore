# IF Explore - Backend

API do IF Explore. Mantém uma cópia local do acervo da Biblioteca Roberval Cardoso,
sincronizada com o catálogo PHL do campus, e a classifica na taxonomia do IF Explore
(áreas, cursos e gêneros literários).

## Stack

- [Python](https://www.python.org/) 3.12 ou mais novo.
- [Django 5.2 LTS](https://docs.djangoproject.com/en/5.2/): ORM, migrações, admin e comandos de sincronização.
- [Django Ninja](https://django-ninja.dev/): rotas da API, validação com Pydantic e documentação OpenAPI.
- [SQLite](https://www.sqlite.org/) em modo WAL, com [FTS5](https://www.sqlite.org/fts5.html) para a busca textual.
- `phl_client`: cliente do catálogo PHL, sem dependências além da biblioteca padrão
  ([documentação](phl_client/api.html)).
- [Gemini](https://ai.google.dev/gemini-api/docs): sugestões da descoberta e explicações
  dos livros, chamado pela API REST com a biblioteca padrão (`catalog/services/gemini.py`).

## Instalação

A partir do diretório `backend/`:

1. Crie e ative um ambiente virtual:
   ```bash
   python -m venv .venv
   ```
   ```bash
   source .venv/bin/activate      # Linux/macOS
   .venv\Scripts\activate         # Windows
   ```
2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
3. Crie o banco (as migrações já trazem as áreas, os cursos e os gêneros):
   ```bash
   python manage.py migrate
   ```
4. Baixe o acervo do PHL (~40 s):
   ```bash
   python manage.py sync_catalog
   ```
5. Para usar o admin, crie um usuário e suba o servidor:
   ```bash
   python manage.py createsuperuser
   ```
   ```bash
   python manage.py runserver
   ```
   O admin fica em <http://localhost:8000/admin/>.

## Configuração

Tudo por variáveis de ambiente; os padrões servem para desenvolvimento, então o
`.env` é opcional. Para mudar algo, copie o modelo e edite:

```bash
cp .env.example .env
```

O `.env` é lido ao iniciar o Django e não é versionado. Variáveis já definidas no
ambiente do sistema (servidor, cron) têm prioridade sobre ele.

| Variável | Padrão | Uso |
|---|---|---|
| `DJANGO_DEBUG` | `true` | Desligue em produção. |
| `DJANGO_SECRET_KEY` | chave de desenvolvimento | Obrigatória com `DJANGO_DEBUG=false`. |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Hosts aceitos, separados por vírgula. |
| `SQLITE_PATH` | `backend/db.sqlite3` | Arquivo do banco. |
| `PHL_CATALOG_URL` | catálogo do campus | Site do PHL. |
| `PHL_PAUSE` | `0.5` | Pausa entre requisições ao PHL, em segundos. |
| `CATALOG_SYNC_MIN_RATIO` | `0.9` | Snapshot com menos títulos que esta fração dos ativos (ou leitura dos exemplares com menos que esta fração dos registros) é recusado. |
| `COPIES_LIVE_MAX_AGE_MINUTES` | `15` | Na página de um livro, exemplares mais velhos que isto são consultados de novo no PHL. |
| `PHL_LIVE_TIMEOUT` | `5` | Tempo limite, em segundos, dessa consulta ao vivo. |
| `CATALOG_LOG_LEVEL` | `INFO` | Nível dos logs da sincronização. |
| `GEMINI_API_KEY` | vazia | Chave da API Gemini. Vazia, a IA fica desligada e a descoberta usa só as regras. Nunca a exponha ao frontend. |
| `GEMINI_MODEL` | `gemini-3.5-flash-lite` | Modelo usado nas duas rotas de IA. |
| `GEMINI_TIMEOUT` | `10` | Tempo limite, em segundos, de cada chamada ao Gemini. |
| `DISCOVERY_RATE` | `10/m` | Limite por IP de `POST /api/discovery` (`número/período`, com `s`, `m`, `h` ou `d`). |
| `EXPLANATION_RATE` | `60/m` | Limite por IP de `GET /api/books/{id}/explanation`. |

## API

Com o servidor rodando, a documentação interativa (OpenAPI) fica em
<http://localhost:8000/api/docs>. As respostas usam camelCase, como o tipo `Book` do
frontend, e valores ausentes saem como `null`.

| Rota | O que devolve |
|---|---|
| `GET /api/areas`, `/api/courses`, `/api/genres` | A taxonomia do IF Explore. |
| `GET /api/books` | Busca e lista livros, paginados (`{items, total, page, pageSize}`). |
| `GET /api/books/{id}` | Um livro completo; os exemplares são consultados ao vivo no PHL se a última consulta tiver mais de 15 min. |
| `GET /api/books/{id}/related` | `{sameAuthor, related}`: outros livros de um autor em comum e os demais por afinidade. |
| `POST /api/recommendations` | `{shelves, areas}` para o perfil do visitante (`{areaIds, courseIds, seedBookIds, genreIds}`). |
| `GET /api/recommendations/candidates` | Títulos para escolher no onboarding (`area`, `course`, `limit`). |
| `POST /api/discovery` | `{source, message, items: [{book, reason}]}`: até 6 títulos do acervo para um pedido em texto livre (`{query, profile?, excludeIds?}`, 3 a 300 caracteres; `excludeIds`, até 60, tira dos candidatos os livros já mostrados, para pedir outras sugestões). |
| `GET /api/books/{id}/explanation` | `{text, generatedAt}`: explicação simplificada do livro gerada por IA (`text` é `null` quando não há). |
| `GET /api/status` | Tamanho do acervo local e as últimas sincronizações. |

Parâmetros de `GET /api/books`:

| Parâmetro | Uso |
|---|---|
| `q` | Texto livre: título, autores, assuntos, sinopse, editora, série, ISBN. Sem diferença de acento ou caixa; aceita início de palavra (`algoritm`). |
| `ids` | Livros pedidos, na ordem dada (até 60); ignora os demais parâmetros. |
| `area`, `course`, `genre` | Filtros pelos ids da taxonomia. |
| `type` | `book`, `ebook`, `audiobook`, `thesis` ou `periodical`. |
| `available` | `true`: só com exemplar livre para empréstimo; `false`: só com exemplares, mas nenhum livre. Situação incerta e títulos sem exemplar ficam fora dos dois. |
| `preferArea` | Áreas cujos livros vêm primeiro (as do visitante). |
| `sort` | `relevance` (padrão com `q`), `popular` (mais exemplares primeiro; padrão sem `q`), `recent` ou `title`. |
| `page`, `pageSize` | Página a partir de 1; até 100 por página (padrão 24). |

Exemplares nos livros (`copies`, `null` até a primeira leitura):

| Campo | Uso |
|---|---|
| `total` | Exemplares do título. |
| `status` | `available` (há exemplar livre), `in_library_use` (nenhum livre, mas há para consulta local), `on_loan` (nenhum livre; há emprestado ou reservado), `unavailable`, `uncertain` (a leitura em lote não permite saber; a página do livro confirma) ou `no_copies` (sem exemplar físico). |
| `available` | Exemplares livres; só vem quando a consulta ao vivo é a leitura mais recente, senão `null`. |
| `updatedAt` | Quando a situação foi lida no PHL. |

O livro completo traz também `loans`, os empréstimos já feitos (`null` até a
consulta ao vivo).

Valores repetidos de um filtro se somam (OU) e filtros diferentes valem juntos (E).
Listas vão com a chave repetida (`?area=technology&area=humanities`); no Axios, use
`paramsSerializer: { indexes: null }` para ele não gerar `area[]=`.

As recomendações seguem as regras que o frontend usava com o acervo fictício e só
incluem livros, e-books, audiolivros e TCCs. Em empates, vêm primeiro os livros com
capa e os com mais exemplares (a biblioteca compra mais exemplares dos títulos mais
procurados, como a bibliografia dos cursos).

### Descoberta com IA

O Gemini nunca busca no catálogo: a API escolhe até 40 candidatos no acervo local
(livros que casam com alguma palavra relevante do pedido e, se o visitante enviar o
perfil, os mais próximos das preferências dele, sem os títulos que ele já escolheu) e
o Gemini só ordena e explica esses candidatos. Ids fora deles são descartados. Sem
chave, em erro, tempo esgotado, cota esgotada ou resposta inválida, a resposta vem
com `source: "rules"`: os primeiros candidatos, sem `reason` e sem `message`.

A explicação de um livro parte só da ficha (título, autores, área, assuntos, sinopse
e notas); títulos sem sinopse nem assuntos não têm explicação. Ela é guardada em
`BookExplanation` e gerada de novo quando a sincronização muda esses dados; no admin,
apagar uma explicação faz a próxima visita gerar outra.

| Rota | Chamadas ao Gemini | Requisições ao PHL |
|---|---|---|
| `POST /api/discovery` | 1 por pedido (0 sem candidatos ou sem chave) | 0 |
| `GET /api/books/{id}/explanation` | 1 na primeira visita ao livro; depois 0 | 0 |

Acima do limite por IP, as duas rotas respondem 429 com `Retry-After`. A contagem usa
o cache do Django (memória local, por processo, na configuração atual). O IP vem de
`X-Forwarded-For` quando o cabeçalho existe; atrás de um proxy reverso, defina
`NINJA_NUM_PROXIES` em `config/settings.py`. Pedidos e prompts não são gravados nem
vão para os logs.

Em desenvolvimento, aponte o frontend para a API com um proxy do Vite (`/api` →
`http://localhost:8000`), sem precisar de CORS.

## Sincronização com o PHL

O PHL é um CGI do campus, que sobe um processo por requisição. Os exemplares têm
duas leituras, de custos bem diferentes:

| Leitura | O que faz | Custo no PHL | Quando |
|---|---|---|---|
| `sync_catalog` | Snapshot dos metadados de todo o acervo e situação resumida dos exemplares (total e situações presentes, do formato decorado do OPAC); atualiza relações, classificação e índice de busca. | ~7 requisições: contagem e exportação do acervo, mais 5 da situação dos exemplares (~1,5 min no total; ver abaixo) | A cada 6 h |
| Consulta ao vivo | Contagem exata de exemplares livres e empréstimos de um título. | 1 requisição | Ao abrir a página do livro, se a última consulta tiver mais de 15 min |

O formato decorado não pagina e o servidor cai em alguns registros defeituosos
(hoje, o registro-esqueleto `01022004448`): os títulos seguintes são relidos pelo
código, o que soma ~6 requisições enquanto o registro existir. Excluí-lo no PHL
elimina esse custo.

Exemplo de agendamento com cron (Linux):

```cron
0 */6 * * * cd /srv/if-explore/backend && .venv/bin/python manage.py sync_catalog
```

No Windows, use o Agendador de Tarefas com os mesmos comandos. Cada execução fica
registrada no admin (Sincronizações), com contagens e erro, e duas execuções do
mesmo tipo não rodam ao mesmo tempo.

Proteções:

- O snapshot é aplicado numa transação: a API vê a versão anterior até o fim.
- Um snapshot muito menor que o banco (resposta truncada) é recusado sem alterar nada.
- Uma falha na leitura dos exemplares (resposta cortada, PHL fora do ar) também não
  aplica nada; a próxima execução tenta de novo.
- A sincronização nunca sobrescreve a contagem exata e os empréstimos da consulta ao vivo.
- Títulos que saem do catálogo são desativados, não apagados.

## Taxonomia e curadoria

O PHL não tem a taxonomia do IF Explore, então ela é derivada na sincronização
(`catalog/services/classification.py`):

- **Área:** CDD 004–006 é sempre Tecnologia; depois vale a área CNPq do registro e,
  sem ela, a CDD.
- **Cursos:** pelos códigos de bibliografia do PHL (campo 079) ou pelo curso do TCC.
  O PHL não publica os nomes dos cursos: os códigos foram inferidos pelos assuntos e
  estão marcados como **não confirmados** até a biblioteca validar no admin.
- **Gêneros:** por palavras-chave nos assuntos (só em CDD literária), prefixos de CDD
  e, para os clássicos brasileiros, autores.

Áreas, cursos e gêneros são editáveis no admin; as mudanças valem a partir da
próxima sincronização do catálogo.

## Estrutura

```text
backend/
├── config/                # settings e rotas (admin e /api/)
├── catalog/               # app do acervo
│   ├── models.py          # livros, autores, assuntos, taxonomia e execuções
│   ├── admin.py           # curadoria da taxonomia; livros só leitura
│   ├── api.py             # rotas da API
│   ├── schemas.py         # contrato JSON (camelCase)
│   ├── services/
│   │   ├── books.py           # filtros, busca e listagem
│   │   ├── recommendations.py # relacionados, prateleiras e candidatos do onboarding
│   │   ├── availability.py    # consulta ao vivo dos exemplares na página do livro
│   │   ├── classification.py  # área, cursos e gêneros (funções puras)
│   │   ├── copy_status.py     # situação do título para o visitante (funções puras)
│   │   ├── search_index.py    # índice FTS5 e busca por relevância
│   │   └── sync.py            # snapshot do catálogo e da situação dos exemplares
│   ├── management/commands/   # sync_catalog
│   ├── migrations/            # inclui o índice FTS5 e a taxonomia inicial
│   └── tests/
└── phl_client/            # cliente do catálogo PHL
```

## Convenções

- Identificadores, nomes de arquivo e mensagens de commit em inglês.
- Docstrings e comentários em português, no formato `Args:`/`Returns:`/`Raises:`.
- Regras sem dependência do Django ficam em funções puras, testáveis sem banco.

## Testes

Os testes não acessam o PHL: usam páginas reais salvas em `phl_client/tests/fixtures/`.

```bash
python manage.py test
```
