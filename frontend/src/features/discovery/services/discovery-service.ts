import { isAxiosError } from 'axios'
import { http } from '../../../lib/http-client'
import {
  ApiContractError,
  list,
  parseBook,
  parseNullableString,
  parseRecord,
  parseString,
} from '../../../services/catalog-parsers'
import { toProfileBody, type PreferenceProfile } from '../../../models/reading-preferences'
import type { DiscoveryItem, DiscoveryResult, DiscoverySource } from '../models/discovery'

/** A API recusou o pedido por excesso de pedidos em pouco tempo (HTTP 429). */
export class RateLimitedError extends Error {
  constructor() {
    super('Limite de pedidos de descoberta atingido')
    this.name = 'RateLimitedError'
  }
}

function isSource(value: string): value is DiscoverySource {
  return value === 'ai' || value === 'rules'
}

function parseItem(value: unknown, path: string): DiscoveryItem {
  const data = parseRecord(value, path)
  return {
    book: parseBook(data.book, `${path}.book`),
    reason: parseNullableString(data.reason, `${path}.reason`),
  }
}

/**
 * Pede à API sugestões do acervo para um pedido em texto livre. A IA escolhe
 * só entre livros do acervo; se ela falhar, a API responde com a seleção por
 * regras (`source: 'rules'`).
 *
 * @param query - Pedido do visitante, já normalizado.
 * @param profile - Preferências salvas, quando o visitante quer considerá-las.
 * @param excludeIds - Livros já sugeridos, para pedir outras sugestões.
 * @param signal - Cancela a requisição quando um novo pedido é feito.
 * @returns Origem, mensagem e até seis livros com o motivo de cada um.
 * @throws RateLimitedError quando a API recusa por excesso de pedidos.
 * @throws ApiContractError quando a resposta sai do contrato.
 */
export async function discover(
  query: string,
  profile: PreferenceProfile | null,
  excludeIds: readonly string[] = [],
  signal?: AbortSignal,
): Promise<DiscoveryResult> {
  const body = {
    query,
    ...(excludeIds.length > 0 ? { excludeIds } : {}),
    ...(profile ? { profile: toProfileBody(profile) } : {}),
  }
  try {
    const { data } = await http.post<unknown>('/discovery', body, { signal })
    const result = parseRecord(data, 'discovery')
    const source = parseString(result.source, 'discovery.source')
    if (!isSource(source)) {
      throw new ApiContractError('discovery.source')
    }
    return {
      source,
      message: parseNullableString(result.message, 'discovery.message'),
      items: list(result.items, 'discovery.items', parseItem),
    }
  } catch (error) {
    if (isAxiosError(error) && error.response?.status === 429) {
      throw new RateLimitedError()
    }
    throw error
  }
}
