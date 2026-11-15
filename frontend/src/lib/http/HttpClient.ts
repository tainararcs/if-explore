import axios, { type AxiosInstance } from 'axios'

import { API_BASE_URL } from '../env'

const sharedAxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  timeout: 15_000,
  headers: {
    Accept: 'application/json',
  },
  // Listas vão com a chave repetida (`area=a&area=b`), como a API espera, e não `area[]=`.
  paramsSerializer: { indexes: null },
})

/**
 * Cliente HTTP compartilhado baseado no Axios.
 */
export class HttpClient {
  /**
   * Expõe a instância configurada do Axios para requisições HTTP padrão.
   *
   * @returns Instância Axios compartilhada.
   */
  public get instance(): AxiosInstance {
    return sharedAxiosInstance
  }
}
