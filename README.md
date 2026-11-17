# IF Explore

Descoberta de leituras no acervo da biblioteca do campus. O visitante conta o que
estuda e do que gosta, e o IF Explore recomenda títulos da biblioteca, mostra se há
exemplar disponível e aceita pedidos em texto livre respondidos com ajuda de IA.

## Tecnologias

| Parte | Stack |
|---|---|
| [Frontend](frontend/) | Vue 3, TypeScript, Vite, Tailwind CSS v4 |
| [Backend](backend/) | Python, Django 5.2, Django Ninja, SQLite (FTS5) |
| Dados | Catálogo PHL do campus, sincronizado a cada 6 h |
| IA | Gemini (opcional) |

## Como executar

São dois processos. Primeiro a API, em `backend/`:

```bash
pip install -r requirements.txt
```

```bash
python manage.py migrate
```

```bash
python manage.py sync_catalog
```

```bash
python manage.py runserver
```

Depois a interface, em `frontend/`:

```bash
npm install
```

```bash
npm run dev
```

Abra <http://localhost:5173>. O Vite repassa `/api` para o backend em
`localhost:8000`. Ambiente virtual, variáveis e agendamento da sincronização estão
nos READMEs de cada parte.

### Com Docker (opcional)

Com Docker e Docker Compose instalados, a API e a interface sobem juntas a partir da
raiz, com recarga automática ao editar o código:

```bash
docker compose up --build
```

Abra <http://localhost:5173>. A API fica em <http://localhost:8000> e aplica as
migrações a cada início. O banco fica no volume `if-explore_db`, separado do
`backend/db.sqlite3` local, e começa vazio. Para baixar o acervo pela primeira vez
(cerca de 1 min e meio), com os containers no ar:

```bash
docker compose exec api python manage.py sync_catalog
```

Ou, para reaproveitar o banco local, com o `runserver` local parado:

```bash
docker compose cp backend/db.sqlite3 api:/data/db.sqlite3
```

Para sincronizar a cada 6 h enquanto os containers rodam:

```bash
docker compose --profile sync up --build
```

As variáveis do `backend/.env` continuam valendo (a chave do Gemini, por exemplo).
Depois de mudar `package.json` ou `requirements.txt`, recrie as imagens e os
`node_modules` do container:

```bash
docker compose up --build --renew-anon-volumes
```

## Estrutura

```text
if-explore/
├── backend/     # API, sincronização com o PHL e admin   → backend/README.md
├── frontend/    # interface web                          → frontend/README.md
├── .claude/     # skills com as especificações de cada tela
└── .github/     # CI do backend e do frontend
```

## Detalhes importantes

- **O acervo é uma cópia local.** O PHL não tem API e não aguenta carga: o backend
  baixa tudo em poucas requisições a cada 6 h e consulta o PHL ao vivo só na página
  de um livro.
- **Contrato compartilhado.** A API responde em camelCase; o frontend espelha os
  tipos em `frontend/src/models/` e valida as respostas. Mudar um lado é mudar o
  outro.
- **Privacidade.** As preferências ficam no navegador do visitante, e ninguém que
  pegou um livro emprestado é identificado.
- **IA com rede de proteção.** O Gemini só escolhe entre livros do acervo local; sem
  chave ou em falha, as sugestões vêm das regras.
- **CI.** Cada push roda lint, tipos e build no frontend, e `check`, migrações e
  testes no backend.
