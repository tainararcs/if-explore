import type { Book } from '../../../models/book'
import { REQUIRED_SEED_BOOKS } from '../../../models/reading-preferences'

/** Passos do onboarding, na ordem em que aparecem. `genres` é opcional. */
export const ONBOARDING_STEPS = ['areas', 'books', 'genres'] as const

export type OnboardingStep = (typeof ONBOARDING_STEPS)[number]

/** Escolhas em andamento, ainda não salvas como preferências. */
export interface OnboardingDraft {
  areaIds: string[]
  courseIds: string[]
  seedBookIds: string[]
  genreIds: string[]
}

export function isOnboardingStep(value: unknown): value is OnboardingStep {
  return ONBOARDING_STEPS.some((step) => step === value)
}

export function stepIndex(step: OnboardingStep): number {
  return ONBOARDING_STEPS.indexOf(step)
}

export function canCompleteAreas(draft: OnboardingDraft): boolean {
  return draft.areaIds.length > 0
}

export function canCompleteBooks(draft: OnboardingDraft): boolean {
  return draft.seedBookIds.length === REQUIRED_SEED_BOOKS
}

/**
 * Calcula o passo mais avançado que o rascunho permite acessar.
 *
 * @param draft - Escolhas atuais.
 * @returns `areas` sem área escolhida, `books` sem os três títulos e
 * `genres` quando os passos obrigatórios estão completos.
 */
export function furthestReachableStep(draft: OnboardingDraft): OnboardingStep {
  if (!canCompleteAreas(draft)) {
    return 'areas'
  }
  return canCompleteBooks(draft) ? 'genres' : 'books'
}

/**
 * Seleciona e ordena os livros oferecidos no passo de escolha de títulos.
 *
 * Livros ligados aos cursos escolhidos aparecem primeiro, seguidos pelos das
 * áreas. Se houver menos títulos que o necessário, completa com o restante do
 * acervo para que o passo sempre possa ser concluído.
 *
 * @param books - Acervo disponível.
 * @param draft - Áreas e cursos escolhidos.
 * @returns Livros candidatos em ordem de relevância.
 */
export function rankCandidateBooks(
  books: readonly Book[],
  draft: Pick<OnboardingDraft, 'areaIds' | 'courseIds'>,
): Book[] {
  const score = (book: Book): number => {
    if (book.courseIds.some((id) => draft.courseIds.includes(id))) {
      return 2
    }
    return draft.areaIds.includes(book.areaId) ? 1 : 0
  }

  const ranked = books
    .map((book) => ({ book, score: score(book) }))
    .filter((entry) => entry.score > 0)
    .sort((a, b) => b.score - a.score)
    .map((entry) => entry.book)

  if (ranked.length >= REQUIRED_SEED_BOOKS) {
    return ranked
  }
  return [...ranked, ...books.filter((book) => !ranked.includes(book))]
}

/**
 * Alterna um valor em uma lista, sem mutar a original.
 *
 * @returns Nova lista com o valor adicionado ou removido.
 */
export function toggleValue(values: readonly string[], value: string): string[] {
  return values.includes(value) ? values.filter((item) => item !== value) : [...values, value]
}
