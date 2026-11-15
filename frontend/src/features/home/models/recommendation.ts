import type { Book } from '../../../models/book'
import type { KnowledgeArea } from '../../../models/taxonomy'

/** Tipos de prateleira; cada um define como o título é apresentado. */
export type ShelfKind = 'forYou' | 'becauseYouChose' | 'moreFromArea' | 'forPleasure'

/**
 * Prateleira de recomendações. `subject` é o nome que completa o título
 * (livro, área ou gênero), quando o tipo exige.
 */
export interface Shelf {
  id: string
  kind: ShelfKind
  subject?: string
  books: Book[]
}

/** Resultado completo das recomendações para a home. */
export interface HomeRecommendations {
  shelves: Shelf[]
  /** Áreas escolhidas, usadas na saudação e no filtro. */
  areas: KnowledgeArea[]
}
