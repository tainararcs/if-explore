import { isAxiosError } from 'axios'
import { http } from '../lib/http-client'
import type { Book, BookDetail } from '../models/book'
import type { Course, KnowledgeArea, LiteraryGenre } from '../models/taxonomy'
import {
  list,
  parseArea,
  parseBookDetail,
  parseBookPage,
  parseCourse,
  parseGenre,
  parseString,
  type BookPage,
} from './catalog-parsers'

/** Limite de ids por consulta aceito pela API. */
const MAX_IDS_PER_REQUEST = 60

/**
 * Guarda a resposta de uma consulta que quase nunca muda (taxonomia) enquanto a
 * página estiver aberta. Uma falha não fica guardada: a próxima chamada tenta de novo.
 */
function cached<T>(load: () => Promise<T>): () => Promise<T> {
  let pending: Promise<T> | null = null
  return () => {
    pending ??= load().catch((error: unknown) => {
      pending = null
      throw error
    })
    return pending
  }
}

/** Grandes áreas do conhecimento, na ordem de exibição. */
export const getKnowledgeAreas = cached(async (): Promise<KnowledgeArea[]> => {
  const { data } = await http.get<unknown>('/areas')
  return list(data, 'areas', parseArea)
})

/** Cursos do campus. */
export const getCourses = cached(async (): Promise<Course[]> => {
  const { data } = await http.get<unknown>('/courses')
  return list(data, 'courses', parseCourse)
})

/** Gêneros literários, na ordem de exibição. */
export const getLiteraryGenres = cached(async (): Promise<LiteraryGenre[]> => {
  const { data } = await http.get<unknown>('/genres')
  return list(data, 'genres', parseGenre)
})

/** Idiomas do acervo, como o catálogo grava, do com mais livros ao com menos. */
export const getLanguages = cached(async (): Promise<string[]> => {
  const { data } = await http.get<unknown>('/languages')
  return list(data, 'languages', parseString)
})

/** Tipos de documento aceitos pelo filtro `type` da API. */
export const BOOK_TYPES = ['book', 'ebook', 'audiobook', 'thesis', 'periodical'] as const
export type BookType = (typeof BOOK_TYPES)[number]

/** Ordens aceitas pela API; sem ordem, relevância com texto e mais exemplares sem. */
export const SORT_ORDERS = ['relevance', 'popular', 'recent', 'year', 'title'] as const
export type SortOrder = (typeof SORT_ORDERS)[number]

/** Filtros da listagem do acervo. Valores do mesmo filtro se somam (OU). */
export interface BookFilters {
  /** Texto livre: título, autores, assuntos, sinopse. */
  query: string
  areaIds?: readonly string[]
  courseIds?: readonly string[]
  genreIds?: readonly string[]
  types?: readonly BookType[]
  /** Só títulos com exemplar disponível para empréstimo. */
  availableOnly?: boolean
  /** Idiomas como o catálogo grava ("Português", "Inglês"). */
  languages?: readonly string[]
  yearFrom?: number | null
  yearTo?: number | null
}

/** Parâmetros da busca no acervo: filtros, ordem e página. */
export interface BookSearchParams extends BookFilters {
  /** Áreas cujos livros vêm primeiro (as do visitante). */
  preferredAreaIds?: readonly string[]
  sort?: SortOrder
  page?: number
  pageSize?: number
  /** Cancela a requisição, por exemplo quando o visitante continua digitando. */
  signal?: AbortSignal
}

/**
 * Converte os filtros nos parâmetros de consulta da API (`GET /books` e
 * `GET /books/facets`), omitindo os vazios.
 *
 * @param filters - Filtros da listagem.
 * @returns Parâmetros prontos para o cliente HTTP.
 */
export function toFilterParams(filters: BookFilters): Record<string, unknown> {
  return {
    q: filters.query || undefined,
    area: filters.areaIds,
    course: filters.courseIds,
    genre: filters.genreIds,
    type: filters.types,
    available: filters.availableOnly ? true : undefined,
    language: filters.languages,
    yearFrom: filters.yearFrom ?? undefined,
    yearTo: filters.yearTo ?? undefined,
  }
}

/**
 * Busca e lista o acervo, paginado.
 *
 * @param params - Texto, filtros, ordem e página.
 * @returns Uma página de resultados com o total encontrado.
 */
export async function searchBooks(params: BookSearchParams): Promise<BookPage> {
  const { data } = await http.get<unknown>('/books', {
    params: {
      ...toFilterParams(params),
      preferArea: params.preferredAreaIds,
      sort: params.sort,
      page: params.page,
      pageSize: params.pageSize,
    },
    signal: params.signal,
  })
  return parseBookPage(data)
}

/**
 * Busca livros pelos identificadores, preservando a ordem recebida.
 *
 * @param ids - Identificadores dos livros.
 * @returns Livros encontrados; ids inexistentes ou fora do acervo são ignorados.
 */
export async function getBooksByIds(ids: readonly string[]): Promise<Book[]> {
  if (ids.length === 0) {
    return []
  }
  const batches = []
  for (let start = 0; start < ids.length; start += MAX_IDS_PER_REQUEST) {
    batches.push(ids.slice(start, start + MAX_IDS_PER_REQUEST))
  }
  const pages = await Promise.all(
    batches.map(async (batch) => parseBookPage((await http.get<unknown>('/books', { params: { ids: batch } })).data)),
  )
  return pages.flatMap((page) => page.items)
}

/**
 * Busca um livro completo. A API consulta a disponibilidade no catálogo da
 * biblioteca quando a informação guardada está velha.
 *
 * @param id - Identificador do livro.
 * @returns O livro, ou `null` quando não existe no acervo.
 */
export async function getBookById(id: string): Promise<BookDetail | null> {
  try {
    const { data } = await http.get<unknown>(`/books/${encodeURIComponent(id)}`)
    return parseBookDetail(data)
  } catch (error) {
    if (isAxiosError(error) && error.response?.status === 404) {
      return null
    }
    throw error
  }
}

export type { BookPage }
