import axios, { type AxiosInstance } from 'axios'

const sharedAxiosInstance = axios.create({
  timeout: 15_000,
  headers: {
    Accept: 'application/json',
  },
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
