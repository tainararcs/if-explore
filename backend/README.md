# IF Explore · Backend

API do IF Explore. Mantém uma cópia local do acervo da biblioteca, sincronizada com
o catálogo PHL do campus, e a classifica na taxonomia do projeto (áreas, cursos e
gêneros literários).

## Tecnologias

- **Python 3.12+** e **Django 5.2 LTS** (ORM, migrações, admin e comandos)
- **Django Ninja**: rotas, validação e documentação OpenAPI
- **SQLite** em modo WAL, com **FTS5** para a busca
- **Gemini**: descoberta com IA e explicações dos livros (opcional)
- **`phl_client`**: cliente do catálogo PHL, só com a biblioteca padrão ([API](phl_client/api.html))

## Como executar

A partir de `backend/`:

```bash
python -m venv .venv
```

```bash
source .venv/bin/activate   # Windows: .venv\Scripts\activate
```

```bash
pip install -r requirements.txt
```

```bash
python manage.py migrate        # cria o banco com a taxonomia inicial
```

```bash
python manage.py sync_catalog   # baixa o acervo do PHL (~1,5 min)
```

```bash
python manage.py runserver
```

| Endereço | O quê |
|---|---|
| <http://localhost:8000/api/docs> | Documentação interativa da API |
| <http://localhost:8000/admin/> | Admin (crie o usuário com `python manage.py createsuperuser`) |

### Configuração

Os padrões servem para desenvolvimento, então o `.env` é opcional. Para mudar algo:

```bash
cp .env.example .env
```

Todas as variáveis e seus padrões estão no [`.env.example`](.env.example). As que
mais importam:

| Variável | Para quê |
|---|---|
| `GEMINI_API_KEY` | Liga a IA. Sem ela, a descoberta usa só as regras. |
| `DJANGO_DEBUG` / `DJANGO_SECRET_KEY` | Em produção: `false` e uma chave própria (obrigatória). |
| `DJANGO_ALLOWED_HOSTS` | Hosts aceitos em produção. |
| `CORS_ALLOWED_ORIGINS` | Só se o frontend estiver em outro domínio. |

Variáveis do ambiente do sistema têm prioridade sobre o `.env`.

### Sincronização agendada

O `sync_catalog` deve rodar a cada 6 h. No Linux, com cron:

```cron
0 */6 * * * cd /srv/if-explore/backend && .venv/bin/python manage.py sync_catalog
```

No Windows, use o Agendador de Tarefas. Cada execução fica registrada no admin
(Sincronizações).

### Testes

```bash
python manage.py test
```

Os testes não acessam a rede: usam páginas reais do PHL salvas em
`phl_client/tests/fixtures/`.

## Estrutura

```text
backend/
├── config/              # settings (variáveis de ambiente) e URLs
├── catalog/             # app do acervo
│   ├── models.py        # livros, taxonomia, sincronizações
│   ├── api.py           # rotas da API
│   ├── schemas.py       # contrato JSON (camelCase)
│   ├── admin.py         # curadoria da taxonomia
│   ├── services/        # regras: sync, busca, recomendações, IA…
│   └── management/commands/
└── phl_client/          # cliente do catálogo PHL
```

Convenções e organização: [docs/project-guidelines.md](docs/project-guidelines.md).

## API

Respostas em camelCase, ausentes como `null`, listas paginadas como
`{items, total, page, pageSize}`. Parâmetros e schemas completos em `/api/docs`.

| Rota | O que devolve |
|---|---|
| `GET /api/areas` · `/courses` · `/genres` | Taxonomia |
| `GET /api/books` | Busca e filtros (`q`, `area`, `course`, `genre`, `type`, `available`, `sort`…) |
| `GET /api/books/{id}` | Livro completo, com exemplares atualizados ao vivo |
| `GET /api/books/{id}/related` | Mesmo autor e livros por afinidade |
| `GET /api/books/{id}/catalog` | Redireciona para a ficha no catálogo oficial |
| `GET /api/books/{id}/explanation` | Explicação simplificada gerada por IA |
| `POST /api/recommendations` | Prateleiras para o perfil do visitante |
| `GET /api/recommendations/candidates` | Títulos para o onboarding |
| `POST /api/discovery` | Até 6 títulos para um pedido em texto livre |
| `GET /api/status` | Tamanho do acervo e últimas sincronizações |

Listas na query string usam a chave repetida (`?area=a&area=b`).

## Detalhes importantes

### O PHL é frágil

O catálogo é um CGI do campus que sobe um processo por requisição. Por isso:

| Leitura | O que traz | Custo no PHL |
|---|---|---|
| `sync_catalog` (a cada 6 h) | Metadados de todo o acervo e situação resumida dos exemplares | ~7 requisições |
| Página do livro | Exemplares livres e empréstimos, ao vivo, se a última leitura tiver mais de 15 min | 1 requisição |
| Link para o catálogo oficial | Abre uma sessão no PHL e redireciona para a ficha | 1 requisição |

Nada no código pode fazer uma requisição por título do acervo.

### Sincronização segura

- O snapshot é aplicado numa única transação: a API lê a versão anterior até o fim.
- Um snapshot muito menor que o acervo atual, ou uma falha no download, é recusado
  sem alterar nada.
- Títulos que saem do catálogo são desativados, não apagados.
- A sincronização nunca sobrescreve a contagem exata da consulta ao vivo.
- Duas execuções do mesmo tipo nunca rodam ao mesmo tempo.

### Disponibilidade

A leitura em lote só diz quais situações existem num título, não quantos exemplares
estão livres. Por isso a API devolve `copies.status` (`available`, `on_loan`,
`uncertain`…), e o número exato só aparece depois da consulta ao vivo. Quem pegou um
livro emprestado nunca é lido nem gravado.

### Taxonomia

O PHL não conhece as áreas, cursos e gêneros do IF Explore: eles são derivados na
sincronização (`catalog/services/classification.py`) e editados no admin. Mudanças
valem na próxima sincronização. Os códigos de curso foram inferidos e ficam **não
confirmados** até a biblioteca validá-los.

A área vem do código CNPq do registro, exceto nas faixas da CDD em que ele costuma
vir errado: computação (004–006) é sempre Tecnologia, e agricultura, criação animal,
veterinária e alimentos (630–639, 664) são sempre Ciências Agrárias. Os prefixos de
CDD dos gêneros são comparados sem o prefixo de coleção do catálogo (`CE`, `R`,
`LIJ`).

### IA

O Gemini nunca busca no catálogo: a API seleciona candidatos do acervo local e a IA
só os ordena e explica. Qualquer falha (sem chave, erro, cota) cai na seleção por
regras. As explicações ficam em cache no banco. As rotas de IA têm limite por IP
(429 acima dele) e os pedidos não são gravados nem logados.
