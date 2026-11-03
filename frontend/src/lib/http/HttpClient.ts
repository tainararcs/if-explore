import axios, { type AxiosInstance } from 'axios'

const sharedAxiosInstance = axios.create({
  // A API fica no mesmo domínio (proxy do Vite em desenvolvimento, proxy reverso em produção).
  baseURL: '/api',
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
