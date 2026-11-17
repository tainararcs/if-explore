# IF Explore · Frontend

Interface do IF Explore: descoberta de leituras no acervo da biblioteca do campus,
com recomendações a partir das preferências do visitante.

## Tecnologias

- **Vue 3** (Composition API) e **TypeScript**
- **Vite**: servidor de desenvolvimento e build
- **Vue Router** e **Vue I18n** (pt-BR)
- **Tailwind CSS v4** sobre os tokens de design do projeto
- **Axios**: chamadas à API
- **ESLint** e **vue-tsc**: lint e tipos

## Como executar

Requer **Node.js 24.22.0**. A partir de `frontend/`:

```bash
npm install
```

```bash
npm run dev
```

A aplicação abre em <http://localhost:5173>. Os dados vêm da API em `backend/`
(veja o [README do backend](../backend/README.md)): em desenvolvimento, o Vite
repassa `/api` para `http://localhost:8000`, sem precisar de CORS. Sem a API, as
telas mostram um erro com a opção de tentar de novo.

### Configuração

Opcional. Copie o [`.env.example`](.env.example) para `.env.local` e ajuste:

| Variável | Padrão | Para quê |
|---|---|---|
| `VITE_API_BASE_URL` | `/api` | Endereço da API no navegador. Fica público no build. |
| `API_PROXY_TARGET` | `http://localhost:8000` | Destino do proxy do Vite, só em desenvolvimento. |
| `WATCH_POLLING` | `false` | `true` verifica os arquivos periodicamente; usado no Docker, onde os eventos do host não chegam. |

### Scripts

| Comando | O que faz |
|---|---|
| `npm run dev` | Servidor de desenvolvimento |
| `npm run build` | Checa os tipos e gera o build de produção |
| `npm run preview` | Serve o build localmente |
| `npm run lint` | ESLint |
| `npm run typecheck` | Checagem de tipos, incluindo os `.vue` |

## Estrutura

```text
frontend/
├── docs/                # diretrizes de projeto e de design
├── public/
└── src/
    ├── features/        # uma pasta por tela: welcome, onboarding, home,
    │                    # book-detail, discovery, errors
    ├── components/      # componentes compartilhados
    ├── composables/     # estado reativo compartilhado
    ├── services/        # acesso à API e validação das respostas
    ├── models/          # contratos (espelham o backend)
    ├── locales/         # textos da interface
    ├── lib/             # utilitários e configuração
    ├── router/
    └── index.css        # tokens de design e estilos base
```

## Detalhes importantes

- **Contrato com a API:** `src/models/book.ts` espelha os schemas do backend, e
  `src/services/catalog-parsers.ts` valida cada resposta. Mudou a API, mude os dois.
- **Regras ficam no backend:** busca, ranking e recomendações vêm prontos da API; a
  disponibilidade é mostrada como `copies.status`, sem interpretação no frontend.
- **Preferências locais:** o perfil de leitura fica só no navegador
  (`localStorage`) e vai no corpo das chamadas de recomendação.
- **Configuração:** leia variáveis por `src/lib/env.ts`, não por `import.meta.env`.
  Nada com prefixo `VITE_` pode ser segredo.
- **Textos:** toda string da interface vai em `src/locales/pt-BR.ts`.

Convenções de código em [docs/project-guidelines.md](docs/project-guidelines.md) e
de visual em [docs/design-guidelines.md](docs/design-guidelines.md).
