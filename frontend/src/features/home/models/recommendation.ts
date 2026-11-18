import type { Book } from '../../../models/book'
import type { KnowledgeArea } from '../../../models/taxonomy'

/** Prateleiras da home, na ordem da página: gêneros, curso e área, parecidos com os escolhidos. */
export const SHELF_KINDS = ['yourGenres', 'forYou', 'fromYourBooks'] as const

/** Tipo de prateleira; cada um define o título. */
export type ShelfKind = (typeof SHELF_KINDS)[number]

/** Indica se o valor é um dos tipos de prateleira do contrato. */
export function isShelfKind(value: string): value is ShelfKind {
  return SHELF_KINDS.some((kind) => kind === value)
}

/**
 * Prateleira de recomendações. `subject` é o nome que completa o título
 * (área ou gênero), quando o tipo exige.
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
