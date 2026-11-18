import type { LocationQuery, LocationQueryRaw } from 'vue-router'
import {
  BOOK_TYPES,
  SORT_ORDERS,
  type BookFilters,
  type BookType,
  type SortOrder,
} from '../../../services/catalog-service'

/** Quantos livros uma opção de filtro traria. */
export interface FacetCount {
  id: string
  count: number
}

/** Contagens dos filtros do catálogo para os filtros atuais. */
export interface CatalogFacets {
  areas: Map<string, number>
  courses: Map<string, number>
  genres: Map<string, number>
  types: Map<string, number>
  /** Do idioma com mais livros ao com menos; só os que existem no acervo. */
  languages: FacetCount[]
  /** Livros com exemplar disponível para empréstimo. */
  available: number
}

/** Filtros e ordem do catálogo, como ficam na URL. */
export interface CatalogState extends Required<Omit<BookFilters, 'yearFrom' | 'yearTo'>> {
  yearFrom: number | null
  yearTo: number | null
  /** `null` usa a ordem padrão da API (relevância com texto, mais exemplares sem). */
  sort: SortOrder | null
}

/** Tipos que o catálogo mostra ao abrir: o que se lê, sem periódicos. */
export const DEFAULT_TYPES: readonly BookType[] = ['book', 'ebook', 'audiobook', 'thesis']

// Na URL, "todos os tipos" precisa de um valor próprio: sem o parâmetro valem os padrões.
const ALL_TYPES = 'any'
const MIN_YEAR = 0
const MAX_YEAR = 9999

function values(raw: LocationQuery[string]): string[] {
  const items = Array.isArray(raw) ? raw : [raw]
  return items.filter((item): item is string => typeof item === 'string' && item !== '')
}

function first(raw: LocationQuery[string]): string {
  return values(raw)[0] ?? ''
}

function year(raw: LocationQuery[string]): number | null {
  const value = Number(first(raw))
  return first(raw) !== '' && Number.isInteger(value) && value >= MIN_YEAR && value <= MAX_YEAR ? value : null
}

function isBookType(value: string): value is BookType {
  return BOOK_TYPES.some((type) => type === value)
}

function isSortOrder(value: string): value is SortOrder {
  return SORT_ORDERS.some((order) => order === value)
}

function sameItems(a: readonly string[], b: readonly string[]): boolean {
  return a.length === b.length && a.every((item) => b.includes(item))
}

/**
 * Lê os filtros da URL. Valores inválidos são ignorados: a URL pode ter sido
 * editada à mão ou vir de uma versão antiga.
 *
 * @param query - Query da rota.
 * @returns Os filtros, com os tipos padrão quando a URL não diz nenhum.
 */
export function readCatalogState(query: LocationQuery): CatalogState {
  const rawTypes = values(query.type)
  const sort = first(query.sort)
  return {
    query: first(query.q),
    areaIds: values(query.area),
    courseIds: values(query.course),
    genreIds: values(query.genre),
    types: rawTypes.length === 0 ? [...DEFAULT_TYPES] : rawTypes.filter(isBookType),
    availableOnly: first(query.available) === '1',
    languages: values(query.language),
    yearFrom: year(query.yearFrom),
    yearTo: year(query.yearTo),
    sort: isSortOrder(sort) ? sort : null,
  }
}

/**
 * Escreve os filtros na URL, omitindo os que estão no valor padrão.
 *
 * @param state - Filtros e ordem do catálogo.
 * @returns Query da rota.
 */
export function writeCatalogState(state: CatalogState): LocationQueryRaw {
  let type: string[] | string | undefined
  if (state.types.length === 0) {
    type = ALL_TYPES
  } else if (!sameItems(state.types, DEFAULT_TYPES)) {
    type = [...state.types]
  }
  return {
    q: state.query || undefined,
    area: state.areaIds.length > 0 ? [...state.areaIds] : undefined,
    course: state.courseIds.length > 0 ? [...state.courseIds] : undefined,
    genre: state.genreIds.length > 0 ? [...state.genreIds] : undefined,
    type,
    available: state.availableOnly ? '1' : undefined,
    language: state.languages.length > 0 ? [...state.languages] : undefined,
    yearFrom: state.yearFrom === null ? undefined : String(state.yearFrom),
    yearTo: state.yearTo === null ? undefined : String(state.yearTo),
    sort: state.sort ?? undefined,
  }
}

/**
 * Quantos filtros estão aplicados além dos padrões (o texto da busca não conta).
 *
 * @param state - Filtros do catálogo.
 * @returns Número mostrado no botão de filtros.
 */
export function countActiveFilters(state: CatalogState): number {
  return (
    state.areaIds.length +
    state.courseIds.length +
    state.genreIds.length +
    state.languages.length +
    (sameItems(state.types, DEFAULT_TYPES) ? 0 : 1) +
    (state.availableOnly ? 1 : 0) +
    (state.yearFrom !== null || state.yearTo !== null ? 1 : 0)
  )
}

/** Filtros no estado padrão, mantendo o texto da busca e a ordem. */
export function clearedFilters(state: CatalogState): CatalogState {
  return {
    ...state,
    areaIds: [],
    courseIds: [],
    genreIds: [],
    types: [...DEFAULT_TYPES],
    availableOnly: false,
    languages: [],
    yearFrom: null,
    yearTo: null,
  }
}
