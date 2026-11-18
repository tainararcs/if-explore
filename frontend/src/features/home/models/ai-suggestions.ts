import type { Book } from '../../../models/book'
import type { ShelfKind } from './recommendation'

/** Livros que um pedido de sugestões pode excluir (o mesmo limite da API). */
export const MAX_EXCLUDED = 60

/**
 * Origem das sugestões: `ai` quando o Gemini escolheu entre os candidatos do
 * acervo; `rules` quando a IA não respondeu e a API escolheu por regras.
 */
export type AiSuggestionSource = 'ai' | 'rules'

/**
 * Livro sugerido, a prateleira da home de onde ele veio (a IA escolhe um de cada)
 * e, quando a IA o escolheu, o motivo.
 */
export interface AiSuggestion {
  book: Book
  kind: ShelfKind
  reason: string | null
}

/** Resposta de `POST /api/recommendations/ai`. */
export interface AiSuggestions {
  source: AiSuggestionSource
  /** Frase da IA para o visitante; `null` na seleção por regras. */
  message: string | null
  items: AiSuggestion[]
}
