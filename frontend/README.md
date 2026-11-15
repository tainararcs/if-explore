# IF Explore - Frontend

## Stack

- [Vue 3](https://vuejs.org/): base da interface, com componentes escritos pela Composition API.
- [TypeScript](https://www.typescriptlang.org/): linguagem de todo o código, com tipagem estática.
- [Vite](https://vite.dev/): servidor de desenvolvimento e build de produção.
- [Vue Router](https://router.vuejs.org/): navegação entre as telas.
- [Vue I18n](https://vue-i18n.intlify.dev/): internacionalização dos textos.
- [Axios](https://axios-http.com/): comunicação com a API.
- [ESLint](https://eslint.org/) e [vue-tsc](https://github.com/vuejs/language-tools): verificação de qualidade e de tipos do código.

## Requisitos 

Para rodar o projeto localmente, você precisará ter o [Node.js](https://nodejs.org/) instalado em sua máquina.
Preferencialmente, utilize a versão 24.22.0 LTS (Long Term Support) do Node.js.

## Instalação

Para instalar as dependências do projeto, siga os passos abaixo:

1. Clone o repositório do projeto:
   ```bash
   git clone https://github.com/tainararcs/if-explore.git
   ```
2. Navegue até o diretório do frontend:
   ```bash
    cd if-explore/frontend
    ```
3. Instale as dependências:
   ```bash
    npm install
    ```

## Rodando o projeto em modo de desenvolvimento

Para iniciar o projeto em modo de desenvolvimento, execute o seguinte comando:

```bash
npm run dev
```

A aplicação estará disponível em [http://localhost:5173](http://localhost:5173).

Os dados do acervo vêm da API do projeto, em `backend/` (veja o
[README do backend](../backend/README.md) para instalar, criar o banco e sincronizar o
acervo). Com a API rodando em `http://localhost:8000`, o servidor do Vite repassa as
chamadas a `/api` para ela, sem precisar de CORS.

As variáveis do frontend estão descritas em [`.env.example`](.env.example). Copie-o para
`.env.local` (ignorado pelo git) e ajuste o que precisar:

| Variável | Padrão | Uso |
|---|---|---|
| `VITE_API_BASE_URL` | `/api` | Endereço base da API usado pelo navegador. Fixado no build e público; em outro domínio, inclua a origem do frontend em `CORS_ALLOWED_ORIGINS` no backend. |
| `VITE_GOOGLE_BOOKS_API_KEY` | vazia | Opcional: liga a prévia de leitura do Google Livros na página do livro (uma consulta por ISBN ao abrir a página; o leitor só carrega no clique). Pública no bundle: use uma chave de navegador restrita à Books API e aos domínios do site. Sem ela, nada é enviado ao Google. |
| `API_PROXY_TARGET` | `http://localhost:8000` | Só em desenvolvimento: destino do proxy do Vite para `/api`. Não vai para o navegador. |

```bash
API_PROXY_TARGET=http://localhost:8001
```

No código, leia a configuração por `src/lib/env.ts`, não por `import.meta.env` direto.

Sem a API, as telas mostram a mensagem de erro com a opção de tentar novamente.

## Compilando o projeto para produção

Para compilar o projeto para produção, execute o seguinte comando:

```bash
npm run build
```

## Servindo a aplicação compilada

Para servir a aplicação compilada, utilize o seguinte comando:

```bash
npm run preview
```

## Validando o código com ESLint

Para validar o código do projeto utilizando o ESLint, execute o seguinte comando:

```bash
npm run lint
```

## Verificando os tipos

Para verificar os tipos do projeto, incluindo os arquivos `.vue`, execute o seguinte comando:

```bash
npm run typecheck
```

## Arquitetura e organização do código

O código é organizado por funcionalidade: cada feature agrupa suas próprias views, componentes, serviços e modelos, e apenas o que é compartilhado entre features fica nos diretórios globais de `src/`.

```
frontend/
├── docs/                   # Diretrizes do projeto
├── public/                 # Arquivos públicos (favicon, etc.)
└── src/                    # Código-fonte do projeto
    ├── features/           # Código organizado por funcionalidade (views, components, services, etc.)
    ├── lib/                # Utilitários e configurações compartilhadas
    ├── router/             # Rotas da aplicação
    ├── App.vue             # Componente raiz
    ├── index.css           # Estilos globais
    └── main.ts             # Ponto de entrada da aplicação
```

A organização completa e as convenções estão descritas em [docs/project-guidelines.md](docs/project-guidelines.md).
