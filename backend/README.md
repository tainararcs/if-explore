# IF Explore - Backend

API do IF Explore. Mantém uma cópia local do acervo da Biblioteca Roberval Cardoso,
sincronizada com o catálogo PHL do campus, e a classifica na taxonomia do IF Explore
(áreas, cursos e gêneros literários).

## Stack

- [Python](https://www.python.org/) 3.12 ou mais novo.
- [Django 5.2 LTS](https://docs.djangoproject.com/en/5.2/): ORM, migrações, admin e comandos de sincronização.
- [SQLite](https://www.sqlite.org/) em modo WAL, com [FTS5](https://www.sqlite.org/fts5.html) para a busca textual.
- `phl_client`: cliente do catálogo PHL, sem dependências além da biblioteca padrão
  ([documentação](phl_client/api.html)).

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

Tudo por variáveis de ambiente; os padrões servem para desenvolvimento.

| Variável | Padrão | Uso |
|---|---|---|
| `DJANGO_DEBUG` | `true` | Desligue em produção. |
| `DJANGO_SECRET_KEY` | chave de desenvolvimento | Obrigatória com `DJANGO_DEBUG=false`. |
| `DJANGO_ALLOWED_HOSTS` | `localhost,127.0.0.1` | Hosts aceitos, separados por vírgula. |
| `SQLITE_PATH` | `backend/db.sqlite3` | Arquivo do banco. |
| `PHL_CATALOG_URL` | catálogo do campus | Site do PHL. |
| `PHL_PAUSE` | `0.5` | Pausa entre requisições ao PHL, em segundos. |
| `CATALOG_SYNC_MIN_RATIO` | `0.9` | Snapshot com menos títulos que esta fração dos ativos é recusado. |
| `COPIES_SYNC_BATCH` | `5000` | Títulos verificados por execução do rodízio de exemplares. |
| `CATALOG_LOG_LEVEL` | `INFO` | Nível dos logs da sincronização. |

## Sincronização com o PHL

O PHL é um CGI do campus, que sobe um processo por requisição. As duas rotinas
respeitam esse custo:

| Comando | O que faz | Custo no PHL | Frequência |
|---|---|---|---|
| `sync_catalog` | Snapshot dos metadados de todo o acervo; atualiza relações, classificação e índice de busca. | 1 requisição (~40 s no total) | Diária |
| `sync_copies` | Exemplares, disponibilidade e empréstimos dos títulos verificados há mais tempo. | 1 requisição por título (~0,7 s) | Diária, em lotes de 5 mil (~1 h); o acervo todo em ~4 noites |

Exemplo de agendamento com cron (Linux), fora do horário de uso da biblioteca:

```cron
0 3 * * *  cd /srv/if-explore/backend && .venv/bin/python manage.py sync_catalog
30 3 * * * cd /srv/if-explore/backend && .venv/bin/python manage.py sync_copies
```

No Windows, use o Agendador de Tarefas com os mesmos comandos. Cada execução fica
registrada no admin (Sincronizações), com contagens e erro, e duas execuções do
mesmo tipo não rodam ao mesmo tempo.

Proteções:

- O snapshot é aplicado numa transação: a API vê a versão anterior até o fim.
- Um snapshot muito menor que o banco (resposta truncada) é recusado sem alterar nada.
- Títulos que saem do catálogo são desativados, não apagados.
- Uma queda do PHL interrompe o rodízio de exemplares; um erro num título isolado é
  contado e o rodízio segue.

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
├── config/                # settings e rotas do Django
├── catalog/               # app do acervo
│   ├── models.py          # livros, autores, assuntos, taxonomia e execuções
│   ├── admin.py           # curadoria da taxonomia; livros só leitura
│   ├── services/
│   │   ├── classification.py  # área, cursos e gêneros (funções puras)
│   │   ├── search_index.py    # índice FTS5 e busca por relevância
│   │   └── sync.py            # snapshot do catálogo e rodízio de exemplares
│   ├── management/commands/   # sync_catalog, sync_copies
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
