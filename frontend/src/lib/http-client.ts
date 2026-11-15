import axios from 'axios'

import { API_BASE_URL } from './env'

/**
 * Instância do Axios compartilhada pelos serviços, já apontada para a API.
 */
export const http = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15_000,
  headers: {
    Accept: 'application/json',
  },
  // Listas vão com a chave repetida (`area=a&area=b`), como a API espera, e não `area[]=`.
  paramsSerializer: { indexes: null },
})
