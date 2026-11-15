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
 * Perfil enviado à API para recomendar ou descobrir, compatível com as
 * preferências salvas (inclusive na forma somente leitura exposta pelo composable).
 */
export interface PreferenceProfile {
  areaIds: readonly string[]
  courseIds: readonly string[]
  seedBookIds: readonly string[]
  genreIds: readonly string[]
}

/**
 * Copia só os campos do perfil, para que a versão e a data das preferências
 * salvas não sejam enviadas à API.
 *
 * @param profile - Preferências salvas ou outro objeto com os campos do perfil.
 * @returns Um objeto apenas com os campos de `PreferenceProfile`.
 */
export function toProfileBody(profile: PreferenceProfile): PreferenceProfile {
  return {
    areaIds: profile.areaIds,
    courseIds: profile.courseIds,
    seedBookIds: profile.seedBookIds,
    genreIds: profile.genreIds,
  }
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
