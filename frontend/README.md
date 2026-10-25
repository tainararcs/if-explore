# IF Explore - Frontend

## Descrição do projeto

TODO: Adicionar descrição do projeto.

## Stack do projeto

Neste projeto, utilizamos as seguintes tecnologias:

- [Vue 3](https://vuejs.org/) - Framework progressivo para construção de interfaces de usuário, utilizado com a Composition API.
- [TypeScript](https://www.typescriptlang.org/) - Superset do JavaScript que adiciona tipagem estática.
- [Vite](https://vite.dev/) - Ferramenta de build rápida para projetos web.
- [Vue Router](https://router.vuejs.org/) - Roteador oficial do Vue.
- [Vue I18n](https://vue-i18n.intlify.dev/) - Biblioteca de internacionalização para Vue.
- [Axios](https://axios-http.com/) - Cliente HTTP.

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

## Estrutura de pastas

A estrutura de pastas do projeto é a seguinte:

```
frontend/
├── docs/                   # Diretrizes do projeto
├── public/                 # Arquivos públicos (favicon, etc.)
├── src/                    # Código-fonte do projeto
│   ├── features/           # Código organizado por funcionalidade (views, components, services, etc.)
│   ├── lib/                # Utilitários e configurações compartilhadas
│   ├── router/             # Rotas da aplicação
│   ├── App.vue             # Componente raiz
│   ├── index.css           # Estilos globais
│   └── main.ts             # Ponto de entrada da aplicação
├── AGENTS.md               # Instruções para agentes de IA
└── CLAUDE.md               # Importa as instruções de agentes para o Claude Code
```

A organização completa e as convenções estão descritas em [docs/project-guidelines.md](docs/project-guidelines.md).
