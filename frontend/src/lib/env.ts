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
 * Um endereço em outro domínio exige incluir a origem do frontend em
 * `CORS_ALLOWED_ORIGINS` no backend.
 */
export const API_BASE_URL = normalizeApiBaseUrl(import.meta.env.VITE_API_BASE_URL)

/**
 * Chave da API do Google Books, usada na prévia de leitura da página do livro.
 * `null` quando ausente: a prévia fica desligada e nada é enviado ao Google.
 * É pública (vai no bundle), por isso deve ser restrita à Books API e aos
 * domínios do site no Google Cloud.
 */
export const GOOGLE_BOOKS_API_KEY = import.meta.env.VITE_GOOGLE_BOOKS_API_KEY?.trim() || null
