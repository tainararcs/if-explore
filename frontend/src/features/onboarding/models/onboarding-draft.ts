import type { Book } from '../../../models/book'
import { REQUIRED_SEED_BOOKS } from '../../../models/reading-preferences'

/**
 * Escolhas em andamento, ainda não salvas como preferências. Os gêneros não ficam
 * aqui: são deduzidos dos títulos escolhidos ao salvar (`inferGenreIds`).
 */
export interface OnboardingDraft {
  areaIds: string[]
  courseIds: string[]
  seedBookIds: string[]
}

/**
 * Recorte do mural de títulos: a mistura de todos os gêneros (com as áreas e os
 * cursos escolhidos), um gênero ou uma área.
 */
export type CandidateFilter =
  | { kind: 'all' }
  | { kind: 'genre'; id: string }
  | { kind: 'area'; id: string }

export const ALL_CANDIDATES: CandidateFilter = { kind: 'all' }

/** Chave estável de um recorte, usada para guardar os candidatos já carregados. */
export function filterKey(filter: CandidateFilter): string {
  return filter.kind === 'all' ? 'all' : `${filter.kind}:${filter.id}`
}

export function canFinish(draft: OnboardingDraft): boolean {
  return draft.seedBookIds.length === REQUIRED_SEED_BOOKS
}

/**
 * Deduz os gêneros de leitura a partir dos títulos escolhidos.
 *
 * @param books - Títulos escolhidos.
 * @param validIds - Gêneros que existem na taxonomia.
 * @returns Gêneros dos títulos, sem repetição, do mais frequente ao menos;
 * em empate, na ordem em que aparecem.
 */
export function inferGenreIds(books: readonly Book[], validIds: readonly string[]): string[] {
  const counts = new Map<string, number>()
  for (const book of books) {
    for (const genreId of book.genreIds) {
      if (validIds.includes(genreId)) {
        counts.set(genreId, (counts.get(genreId) ?? 0) + 1)
      }
    }
  }
  return [...counts.entries()].sort((a, b) => b[1] - a[1]).map(([genreId]) => genreId)
}

/**
 * Alterna um valor em uma lista, sem mutar a original.
 *
 * @returns Nova lista com o valor adicionado ou removido.
 */
export function toggleValue(values: readonly string[], value: string): string[] {
  return values.includes(value) ? values.filter((item) => item !== value) : [...values, value]
}
