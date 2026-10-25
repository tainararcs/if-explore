import { createRouter, createWebHistory } from 'vue-router'

/**
 * Centraliza as rotas públicas da aplicação.
 */
export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/',
      redirect: '/home',
    },
    {
      path: '/home',
      component: () => import('../features/home/views/HomeView.vue'),
    },
    {
      path: '/403',
      component: () => import('../features/errors/views/ForbiddenView.vue'),
    },
    {
      path: '/500',
      component: () => import('../features/errors/views/InternalServerErrorView.vue'),
    },
    {
      path: '/:pathMatch(.*)*',
      component: () => import('../features/errors/views/NotFoundView.vue'),
    },
  ],
})
