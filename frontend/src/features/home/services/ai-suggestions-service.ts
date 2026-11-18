import { isAxiosError } from 'axios'
import { http } from '../../../lib/http-client'
import { toProfileBody, type PreferenceProfile } from '../../../models/reading-preferences'
import {
  ApiContractError,
  list,
  parseBook,
  parseNullableString,
  parseRecord,
  parseString,
} from '../../../services/catalog-parsers'
import type { AiSuggestion, AiSuggestions, AiSuggestionSource } from '../models/ai-suggestions'

/** A API recusou o pedido por excesso de pedidos em pouco tempo (HTTP 429). */
export class RateLimitedError extends Error {
  constructor() {
    super('Limite de pedidos de sugestões atingido')
    this.name = 'RateLimitedError'
  }
}

function isSource(value: string): value is AiSuggestionSource {
  return value === 'ai' || value === 'rules'
}

function parseItem(value: unknown, path: string): AiSuggestion {
  const data = parseRecord(value, path)
  return {
    book: parseBook(data.book, `${path}.book`),
    reason: parseNullableString(data.reason, `${path}.reason`),
  }
}

/**
 * Pede à API uma seleção de livros do acervo escolhida pela IA para o perfil, com
 * o motivo de cada um. Vai para a IA só o perfil anônimo (nomes de áreas, cursos
 * e gêneros e os títulos escolhidos); se ela falhar, a API responde com a seleção
 * por regras (`source: 'rules'`).
 *
 * @param profile - Preferências salvas do visitante.
 * @param excludeIds - Livros que não devem voltar (já mostrados na home ou sugeridos).
 * @param signal - Cancela a requisição quando a tela é fechada.
 * @returns Origem, mensagem e até seis livros com o motivo de cada um.
 * @throws RateLimitedError quando a API recusa por excesso de pedidos.
 * @throws ApiContractError quando a resposta sai do contrato.
 */
export async function getAiSuggestions(
  profile: PreferenceProfile,
  excludeIds: readonly string[],
  signal?: AbortSignal,
): Promise<AiSuggestions> {
  try {
    const { data } = await http.post<unknown>(
      '/recommendations/ai',
      { ...toProfileBody(profile), excludeIds },
      { signal },
    )
    const result = parseRecord(data, 'suggestions')
    const source = parseString(result.source, 'suggestions.source')
    if (!isSource(source)) {
      throw new ApiContractError('suggestions.source')
    }
    return {
      source,
      message: parseNullableString(result.message, 'suggestions.message'),
      items: list(result.items, 'suggestions.items', parseItem),
    }
  } catch (error) {
    if (isAxiosError(error) && error.response?.status === 429) {
      throw new RateLimitedError()
    }
    throw error
  }
}
