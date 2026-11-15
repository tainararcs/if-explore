/**
 * Configuração do frontend lida das variáveis de ambiente do Vite.
 *
 * Só variáveis com o prefixo `VITE_` chegam aqui, e todas vão para o bundle
 * público: nunca coloque segredos nelas. Os valores ficam em `.env.local`
 * (veja `.env.example`) e são fixados no momento do build.
 */

const DEFAULT_API_BASE_URL = '/api'

/**
 * Normaliza o endereço base da API, removendo espaços e barras finais.
 *
 * @param value - Valor bruto da variável de ambiente, possivelmente ausente.
 * @returns O endereço informado ou `/api` (mesmo domínio) quando vazio.
 */
function normalizeApiBaseUrl(value: string | undefined): string {
  const trimmed = value?.trim().replace(/\/+$/, '') ?? ''
  return trimmed || DEFAULT_API_BASE_URL
}

/**
 * Endereço base da API do projeto. Por padrão `/api`, no mesmo domínio do
 * frontend (proxy do Vite em desenvolvimento, proxy reverso em produção).
 * Um endereço em outro domínio exige CORS habilitado no backend.
 */
export const API_BASE_URL = normalizeApiBaseUrl(import.meta.env.VITE_API_BASE_URL)
