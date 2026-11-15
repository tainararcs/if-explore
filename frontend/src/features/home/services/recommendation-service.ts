import { http } from '../../../lib/http-client'
import {
  ApiContractError,
  list,
  parseArea,
  parseBook,
  parseNullableString,
  parseRecord,
  parseString,
} from '../../../services/catalog-parsers'
import { toProfileBody, type PreferenceProfile } from '../../../models/reading-preferences'
import type { HomeRecommendations, Shelf, ShelfKind } from '../models/recommendation'

const SHELF_KINDS: readonly ShelfKind[] = ['forYou', 'becauseYouChose', 'moreFromArea', 'forPleasure']

function isShelfKind(value: string): value is ShelfKind {
  return SHELF_KINDS.some((kind) => kind === value)
}

function parseShelf(value: unknown, path: string): Shelf {
  const data = parseRecord(value, path)
  const kind = parseString(data.kind, `${path}.kind`)
  if (!isShelfKind(kind)) {
    throw new ApiContractError(`${path}.kind`)
  }
  const subject = parseNullableString(data.subject, `${path}.subject`)
  return {
    id: parseString(data.id, `${path}.id`),
    kind,
    ...(subject === null ? {} : { subject }),
    books: list(data.books, `${path}.books`, parseBook),
  }
}

/**
 * Obtém as prateleiras da home para as preferências do visitante. As regras de
 * recomendação ficam na API, que considera o acervo inteiro.
 *
 * @param profile - Preferências salvas do visitante.
 * @returns Prateleiras (só as com livros suficientes) e as áreas escolhidas.
 */
export async function getHomeRecommendations(
  profile: PreferenceProfile,
): Promise<HomeRecommendations> {
  const { data } = await http.post<unknown>('/recommendations', toProfileBody(profile))
  const body = parseRecord(data, 'recommendations')
  return {
    shelves: list(body.shelves, 'recommendations.shelves', parseShelf),
    areas: list(body.areas, 'recommendations.areas', parseArea),
  }
}
