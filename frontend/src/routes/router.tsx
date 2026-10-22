import { createBrowserRouter, redirect } from 'react-router'
import { ForbiddenView } from '../features/errors/views/ForbiddenView'
import { InternalServerErrorView } from '../features/errors/views/InternalServerErrorView'
import { NotFoundView } from '../features/errors/views/NotFoundView'
import { HomeView } from '../features/home/views/HomeView'

/**
 * Centraliza as rotas públicas da aplicação.
 */
export const router = createBrowserRouter([
  {
    path: '/',
    loader: () => redirect('/home'),
  },
  {
    path: '/home',
    element: <HomeView />,
  },
  {
    path: '/403',
    element: <ForbiddenView />,
  },
  {
    path: '/500',
    element: <InternalServerErrorView />,
  },
  {
    path: '*',
    element: <NotFoundView />,
  },
])
