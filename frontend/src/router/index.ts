import { createRouter, createWebHistory } from 'vue-router'
import { useReadingPreferences } from '../composables/useReadingPreferences'
import { i18n } from '../lib/i18n'

declare module 'vue-router' {
  interface RouteMeta {
    /** Chave de tradução usada no título do documento. */
    titleKey?: string
  }
}

const RESTORE_TIMEOUT_MS = 1500
const RESTORE_POLL_MS = 50

/**
 * Aguarda a página crescer o bastante para rolar até `top`. As telas carregam
 * dados de forma assíncrona; sem esperar, voltar pelo histórico cairia no topo.
 * Desiste após um tempo e deixa o navegador rolar até onde for possível.
 */
function waitForScrollableHeight(top: number): Promise<void> {
  const deadline = Date.now() + RESTORE_TIMEOUT_MS
  return new Promise((resolve) => {
    const check = () => {
      const fits = document.documentElement.scrollHeight - window.innerHeight >= top
      if (fits || Date.now() >= deadline) {
        resolve()
        return
      }
      window.setTimeout(check, RESTORE_POLL_MS)
    }
    check()
  })
}

/**
 * Centraliza as rotas públicas da aplicação.
 */
export const router = createRouter({
  history: createWebHistory(),
  // Nova página começa no topo; voltar restaura a posição. Mudanças só na query
  // (busca, passo do onboarding) mantêm a rolagem atual.
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      return waitForScrollableHeight(savedPosition.top).then(() => savedPosition)
    }
    return to.path === from.path ? false : { top: 0 }
  },
  routes: [
    {
      path: '/',
      component: () => import('../features/welcome/views/WelcomeView.vue'),
      meta: { titleKey: 'routes.welcome' },
    },
    {
      path: '/onboarding',
      component: () => import('../features/onboarding/views/TasteOnboardingView.vue'),
      meta: { titleKey: 'routes.onboarding' },
    },
    {
      path: '/home',
      component: () => import('../features/home/views/HomeView.vue'),
      meta: { titleKey: 'routes.home' },
      // Sem preferências não há recomendações: o visitante volta às boas-vindas.
      beforeEnter: () => useReadingPreferences().hasPreferences.value || '/',
    },
    {
      path: '/books/:id',
      component: () => import('../features/book-detail/views/BookDetailView.vue'),
      meta: { titleKey: 'routes.book' },
    },
    {
      path: '/403',
      component: () => import('../features/errors/views/ForbiddenView.vue'),
      meta: { titleKey: 'routes.forbidden' },
    },
    {
      path: '/500',
      component: () => import('../features/errors/views/InternalServerErrorView.vue'),
      meta: { titleKey: 'routes.serverError' },
    },
    {
      path: '/:pathMatch(.*)*',
      component: () => import('../features/errors/views/NotFoundView.vue'),
      meta: { titleKey: 'routes.notFound' },
    },
  ],
})

router.afterEach((to) => {
  const appName = i18n.global.t('common.appName')
  document.title = to.meta.titleKey ? `${i18n.global.t(to.meta.titleKey)} · ${appName}` : appName
})
