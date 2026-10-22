import { RouterProvider } from 'react-router'
import { router } from './routes/router'

/**
 * Disponibiliza o roteador principal da aplicação.
 */
function App() {
  return <RouterProvider router={router} />
}

export default App
