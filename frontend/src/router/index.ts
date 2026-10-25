import { createRouter, createWebHistory } from 'vue-router'
import { useReadingPreferences } from '../composables/useReadingPreferences'
import { i18n } from '../lib/i18n'

declare module 'vue-router' {
  interface RouteMeta {
    /** Chave de tradução usada no título do documento. */
    titleKey?: string
  }
}

/**
 * Centraliza as rotas públicas da aplicação.
 */
export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      component: () => import('../features/welcome/views/WelcomeView.vue'),
      meta: { titleKey: 'routes.welcome' },
    },
    {
      path: '/home',
      component: () => import('../features/home/views/HomeView.vue'),
      meta: { titleKey: 'routes.home' },
      // Sem preferências não há recomendações: o visitante volta às boas-vindas.
      beforeEnter: () => useReadingPreferences().hasPreferences.value || '/',
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
