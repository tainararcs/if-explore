import type { Book } from '../../../models/book'

/** Tamanho aceito para o pedido, depois de juntar os espaços (o mesmo da API). */
export const MIN_QUERY_LENGTH = 3
export const MAX_QUERY_LENGTH = 300

/**
 * Origem das sugestões: `ai` quando o Gemini escolheu entre os candidatos do
 * acervo; `rules` quando a IA não respondeu e a API escolheu por regras.
 */
export type DiscoverySource = 'ai' | 'rules'

/** Livro sugerido e, nas sugestões da IA, o motivo da escolha. */
export interface DiscoveryItem {
  book: Book
  reason: string | null
}

/** Resposta de `POST /api/discovery`. */
export interface DiscoveryResult {
  source: DiscoverySource
  /** Frase da IA para o visitante; `null` na seleção por regras. */
  message: string | null
  items: DiscoveryItem[]
}

/**
 * Preferências enviadas junto com o pedido, compatíveis com as salvas no
 * navegador (inclusive na forma somente leitura exposta pelo composable).
 */
export interface DiscoveryProfile {
  areaIds: readonly string[]
  courseIds: readonly string[]
  seedBookIds: readonly string[]
  genreIds: readonly string[]
}

/**
 * Junta espaços repetidos e remove os das pontas, como a API faz antes de
 * validar o tamanho do pedido.
 */
export function normalizeQuery(text: string): string {
  return text.trim().replace(/\s+/g, ' ')
}

/** Indica se o pedido tem o tamanho aceito pela API. */
export function isValidQuery(text: string): boolean {
  const length = normalizeQuery(text).length
  return length >= MIN_QUERY_LENGTH && length <= MAX_QUERY_LENGTH
}
