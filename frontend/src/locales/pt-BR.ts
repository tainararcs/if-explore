/**
 * Textos da interface em português do Brasil, agrupados por funcionalidade.
 */
export const ptBR = {
  common: {
    appName: 'IF Explore',
    libraryName: 'Biblioteca Roberval Cardoso',
    institution: 'IF Sudeste MG – Campus Barbacena',
    brandHomeLabel: 'IF Explore, página inicial',
    opensInNewTab: '(abre em nova aba)',
    coverLabel: 'Capa de {title}, de {author}',
    theme: {
      useLight: 'Ativar tema claro',
      useDark: 'Ativar tema escuro',
    },
  },
  routes: {
    welcome: 'Boas-vindas',
    home: 'Suas recomendações',
    forbidden: 'Acesso negado',
    serverError: 'Erro interno',
    notFound: 'Página não encontrada',
  },
  welcome: {
    eyebrow: 'Biblioteca Roberval Cardoso · IF Sudeste MG – Barbacena',
    title: 'Sua próxima leitura já está {emphasis} do campus.',
    titleEmphasis: 'na estante',
    lead: 'O IF Explore sugere livros do acervo da biblioteca a partir da sua área de estudo e do seu gosto. Leva cerca de um minuto e não precisa de login.',
    start: 'Descobrir minhas leituras',
    viewRecommendations: 'Ver minhas recomendações',
    restart: 'Refazer minhas escolhas',
    privacy: 'Suas preferências ficam salvas apenas neste navegador.',
    howItWorks: {
      title: 'Como funciona',
      areas: {
        title: 'Escolha suas áreas',
        text: 'Conte o que você estuda ou quer estudar.',
      },
      books: {
        title: 'Marque três títulos',
        text: 'Escolha livros que chamam sua atenção.',
      },
      recommendations: {
        title: 'Receba recomendações',
        text: 'Descubra leituras do acervo feitas para você.',
      },
    },
    officialSite: 'Acessar o site oficial da biblioteca',
  },
}

/** Estrutura das mensagens usada para tipar a configuração do vue-i18n. */
export type MessageSchema = typeof ptBR
