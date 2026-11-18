import { toProfileBody, type PreferenceProfile } from '../../../models/reading-preferences'
import { isShelfKind, type ShelfKind } from '../models/recommendation'

const STORAGE_KEY = 'if-explore:home-ai-suggestions'

/** Sugestão guardada: só o id do livro, a prateleira e o motivo; o livro é recarregado da API. */
export interface StoredPick {
  id: string
  kind: ShelfKind
  reason: string | null
}

/** Última prateleira da IA na sessão e os livros que ela já mostrou. */
export interface StoredSuggestions {
  message: string | null
  picks: StoredPick[]
  /** Todos os livros já sugeridos na sessão, para "outras sugestões" não repetir. */
  seenIds: string[]
}

interface StoredRecord extends StoredSuggestions {
  profileKey: string
}

function profileKey(profile: PreferenceProfile): string {
  return JSON.stringify(toProfileBody(profile))
}

function isStringArray(value: unknown): value is string[] {
  return Array.isArray(value) && value.every((item) => typeof item === 'string')
}

function isPick(value: unknown): value is StoredPick {
  if (typeof value !== 'object' || value === null) {
    return false
  }
  const record: Record<string, unknown> = { ...value }
  return (
    typeof record.id === 'string' &&
    typeof record.kind === 'string' &&
    isShelfKind(record.kind) &&
    (record.reason === null || typeof record.reason === 'string')
  )
}

function parse(raw: string): StoredRecord | null {
  const value: unknown = JSON.parse(raw)
  if (typeof value !== 'object' || value === null) {
    return null
  }
  const record: Record<string, unknown> = { ...value }
  const { profileKey: key, message, picks, seenIds } = record
  if (
    typeof key !== 'string' ||
    !(message === null || typeof message === 'string') ||
    !Array.isArray(picks) ||
    !picks.every(isPick) ||
    !isStringArray(seenIds)
  ) {
    return null
  }
  return { profileKey: key, message, picks, seenIds }
}

/**
 * Lê a prateleira da IA guardada nesta sessão, para que voltar à home não peça
 * outra chamada à IA. Vale só para o mesmo perfil: mudar as preferências descarta.
 *
 * @param profile - Preferências atuais do visitante.
 * @returns As sugestões guardadas, ou `null` sem dados válidos para o perfil.
 */
export function loadAiSuggestions(profile: PreferenceProfile): StoredSuggestions | null {
  try {
    const raw = window.sessionStorage.getItem(STORAGE_KEY)
    const record = raw === null ? null : parse(raw)
    if (record === null || record.profileKey !== profileKey(profile)) {
      return null
    }
    return { message: record.message, picks: record.picks, seenIds: record.seenIds }
  } catch {
    return null
  }
}

/**
 * Guarda a prateleira da IA para o restante da sessão.
 *
 * @param profile - Preferências usadas no pedido.
 * @param suggestions - Mensagem, sugestões e livros já vistos.
 */
export function saveAiSuggestions(profile: PreferenceProfile, suggestions: StoredSuggestions): void {
  try {
    const record: StoredRecord = { profileKey: profileKey(profile), ...suggestions }
    window.sessionStorage.setItem(STORAGE_KEY, JSON.stringify(record))
  } catch {
    // Armazenamento indisponível: a prateleira vale só enquanto a tela estiver aberta.
  }
}
