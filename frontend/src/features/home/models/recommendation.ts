import type { Book } from '../../../models/book'
import type { KnowledgeArea } from '../../../models/taxonomy'

/**
 * Perfil usado para recomendar, compatível com as preferências salvas
 * (inclusive na forma somente leitura exposta pelo composable).
 */
export interface RecommendationProfile {
  areaIds: readonly string[]
  courseIds: readonly string[]
  seedBookIds: readonly string[]
  genreIds: readonly string[]
}

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
