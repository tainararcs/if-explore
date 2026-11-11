const STORAGE_KEY = 'if-explore:discovery-recent'

/** Quantos pedidos recentes ficam guardados. */
export const MAX_RECENT_REQUESTS = 5

/**
 * Lê os pedidos recentes guardados no navegador, do mais novo ao mais antigo.
 *
 * Dados corrompidos ou armazenamento indisponível (modo privado, bloqueio)
 * resultam numa lista vazia.
 */
export function loadRecentRequests(): string[] {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    const value: unknown = raw === null ? [] : JSON.parse(raw)
    if (!Array.isArray(value)) {
      return []
    }
    return value.filter((item): item is string => typeof item === 'string').slice(0, MAX_RECENT_REQUESTS)
  } catch {
    return []
  }
}

/**
 * Põe o pedido no início da lista, sem repetir (ignorando maiúsculas), e guarda
 * no máximo `MAX_RECENT_REQUESTS`.
 *
 * @param requests - Lista atual.
 * @param query - Pedido recém-feito, já normalizado.
 * @returns A nova lista; ela vale para a tela mesmo se a gravação falhar.
 */
export function addRecentRequest(requests: readonly string[], query: string): string[] {
  const key = query.toLocaleLowerCase('pt-BR')
  const next = [query, ...requests.filter((item) => item.toLocaleLowerCase('pt-BR') !== key)].slice(
    0,
    MAX_RECENT_REQUESTS,
  )
  saveRecentRequests(next)
  return next
}

/** Apaga os pedidos recentes do navegador. */
export function clearRecentRequests(): void {
  saveRecentRequests([])
}

function saveRecentRequests(requests: readonly string[]): void {
  try {
    if (requests.length === 0) {
      window.localStorage.removeItem(STORAGE_KEY)
    } else {
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(requests))
    }
  } catch {
    // Sem armazenamento, os pedidos recentes valem só até a página fechar.
  }
}
