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
    onboarding: 'Descobrir minhas leituras',
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
  onboarding: {
    back: 'Voltar',
    loading: 'Carregando opções…',
    error: 'Não foi possível carregar as opções do acervo.',
    retry: 'Tentar novamente',
    recommend: 'Me recomende',
    progress: {
      step: 'Passo {current} de {total}',
      refine: 'Etapa extra',
    },
    areas: {
      title: 'O que você estuda ou quer estudar?',
      helper: 'Escolha uma ou mais áreas. Se fizer um curso do campus, marque-o também.',
      legend: 'Áreas do conhecimento',
      coursesQuestion: 'Faz algum destes cursos? (opcional)',
      hint: 'Escolha pelo menos uma área para continuar.',
      selected: 'Nenhuma área escolhida | 1 área escolhida | {n} áreas escolhidas',
      continue: 'Continuar',
    },
    books: {
      title: 'Escolha três títulos que chamam sua atenção.',
      helper: 'Eles serão o ponto de partida das suas recomendações.',
      filterLegend: 'Filtrar títulos por área',
      allAreas: 'Todas',
      missing: 'Escolha mais títulos | Falta 1 título | Faltam {n} títulos',
      complete: 'Pronto! Peça suas recomendações ou refine seus gostos.',
      refine: 'Refinar com gêneros literários',
    },
    genres: {
      title: 'E fora da sala de aula, o que você gosta de ler?',
      helper: 'Opcional: escolha quantos gêneros quiser.',
      legend: 'Gêneros literários',
      selected: 'Nenhum gênero escolhido | 1 gênero escolhido | {n} gêneros escolhidos',
    },
  },
  home: {
    eyebrow: 'Para você',
    title: 'Suas recomendações',
    basis: 'Com base em {areas} e nos títulos que você escolheu.',
    adjustPreferences: 'Ajustar preferências',
    filterLegend: 'Filtrar por área',
    allAreas: 'Todas',
    loading: 'Carregando recomendações…',
    error: 'Não foi possível carregar suas recomendações.',
    retry: 'Tentar novamente',
    emptyFilter: 'Nenhuma recomendação para esta área por enquanto.',
    shelves: {
      forYou: 'Escolhidos para você',
      becauseYouChose: 'Porque você escolheu {subject}',
      moreFromArea: 'Mais de {subject}',
      forPleasure: 'Para ler por prazer: {subject}',
    },
    shelf: {
      previous: 'Ver livros anteriores',
      next: 'Ver próximos livros',
    },
    availability: {
      available: 'Disponível',
      borrowed: 'Emprestado',
    },
    search: {
      label: 'Buscar no acervo',
      placeholder: 'Título, autor ou assunto',
      clear: 'Limpar busca',
      clearAction: 'Limpar busca',
      results:
        'Nenhum resultado para “{query}” | 1 resultado para “{query}” | {n} resultados para “{query}”',
      emptyTitle: 'Nenhum livro encontrado',
      emptyText: 'Confira a grafia, tente outras palavras ou remova o filtro de área.',
    },
  },
}

/** Estrutura das mensagens usada para tipar a configuração do vue-i18n. */
export type MessageSchema = typeof ptBR
