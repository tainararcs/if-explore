import type { Book } from '../../../models/book'

/** Livros que um pedido de sugestões pode excluir (o mesmo limite da API). */
export const MAX_EXCLUDED = 60

/**
 * Origem das sugestões: `ai` quando o Gemini escolheu entre os candidatos do
 * acervo; `rules` quando a IA não respondeu e a API escolheu por regras.
 */
export type AiSuggestionSource = 'ai' | 'rules'

/** Livro sugerido e, nas sugestões da IA, o motivo da escolha. */
export interface AiSuggestion {
  book: Book
  reason: string | null
}

/** Resposta de `POST /api/recommendations/ai`. */
export interface AiSuggestions {
  source: AiSuggestionSource
  /** Frase da IA para o visitante; `null` na seleção por regras. */
  message: string | null
  items: AiSuggestion[]
}
