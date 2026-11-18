import { http } from '../../../lib/http-client'
import { list, parseNumber, parseRecord, parseString } from '../../../services/catalog-parsers'
import { toFilterParams, type BookFilters } from '../../../services/catalog-service'
import type { CatalogFacets, FacetCount } from '../models/catalog-filters'

function parseCount(value: unknown, path: string): FacetCount {
  const data = parseRecord(value, path)
  return { id: parseString(data.id, `${path}.id`), count: parseNumber(data.count, `${path}.count`) }
}

function toMap(value: unknown, path: string): Map<string, number> {
  return new Map(list(value, path, parseCount).map((item) => [item.id, item.count]))
}

/**
 * Conta quantos livros cada opção de filtro traria com os filtros atuais. Cada
 * filtro é contado sem ele mesmo, porque as opções de um filtro se somam.
 *
 * @param filters - Texto e filtros aplicados na listagem.
 * @param signal - Cancela a requisição quando os filtros mudam de novo.
 * @returns Contagens por área, curso, gênero, tipo e idioma, e os disponíveis.
 */
export async function getCatalogFacets(filters: BookFilters, signal?: AbortSignal): Promise<CatalogFacets> {
  const { data } = await http.get<unknown>('/books/facets', { params: toFilterParams(filters), signal })
  const body = parseRecord(data, 'facets')
  return {
    areas: toMap(body.areas, 'facets.areas'),
    courses: toMap(body.courses, 'facets.courses'),
    genres: toMap(body.genres, 'facets.genres'),
    types: toMap(body.types, 'facets.types'),
    languages: list(body.languages, 'facets.languages', parseCount),
    available: parseNumber(body.available, 'facets.available'),
  }
}
