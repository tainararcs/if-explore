/** Quantidade de títulos que o visitante escolhe na personalização. */
export const REQUIRED_SEED_BOOKS = 3

/**
 * Preferências de leitura do visitante, salvas apenas no navegador.
 */
export interface ReadingPreferences {
  version: 1
  areaIds: string[]
  courseIds: string[]
  /** Títulos escolhidos pelo visitante que servem de base para as recomendações. */
  seedBookIds: string[]
  genreIds: string[]
  /** Data da última gravação em formato ISO 8601. */
  updatedAt: string
}

/**
 * Indica se as preferências bastam para gerar recomendações.
 *
 * @param preferences - Preferências salvas, se houver.
 * @returns `true` quando há ao menos uma área e os títulos obrigatórios.
 */
export function isCompletePreferences(preferences: ReadingPreferences | null): boolean {
  return (
    preferences !== null &&
    preferences.areaIds.length > 0 &&
    preferences.seedBookIds.length === REQUIRED_SEED_BOOKS
  )
}
