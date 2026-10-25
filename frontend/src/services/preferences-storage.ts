import type { ReadingPreferences } from '../models/reading-preferences'

const STORAGE_KEY = 'if-explore:preferences'

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === 'string')
}

/**
 * Valida dados desconhecidos lidos do armazenamento.
 *
 * @param value - Valor obtido do JSON salvo.
 * @returns As preferências quando o formato é válido; caso contrário, `null`.
 */
function parsePreferences(value: unknown): ReadingPreferences | null {
  if (typeof value !== 'object' || value === null) {
    return null
  }

  const record: Record<string, unknown> = { ...value }
  const { version, areaIds, courseIds, seedBookIds, genreIds, updatedAt } = record

  if (
    version !== 1 ||
    !isStringArray(areaIds) ||
    !isStringArray(courseIds) ||
    !isStringArray(seedBookIds) ||
    !isStringArray(genreIds) ||
    typeof updatedAt !== 'string'
  ) {
    return null
  }

  return { version, areaIds, courseIds, seedBookIds, genreIds, updatedAt }
}

/**
 * Lê as preferências salvas no `localStorage`.
 *
 * Dados corrompidos ou armazenamento indisponível (modo privado, bloqueio)
 * são tratados como ausência de preferências.
 *
 * @returns As preferências válidas ou `null`.
 */
export function loadPreferences(): ReadingPreferences | null {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    return raw === null ? null : parsePreferences(JSON.parse(raw))
  } catch {
    return null
  }
}

/**
 * Grava as preferências no `localStorage`.
 *
 * @param preferences - Preferências a salvar.
 * @returns `true` quando a gravação foi concluída.
 */
export function savePreferences(preferences: ReadingPreferences): boolean {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences))
    return true
  } catch {
    return false
  }
}

/**
 * Remove as preferências salvas, ignorando falhas do armazenamento.
 */
export function clearPreferences(): void {
  try {
    window.localStorage.removeItem(STORAGE_KEY)
  } catch {
    // Sem armazenamento disponível não há o que remover.
  }
}
