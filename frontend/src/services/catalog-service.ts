import { isAxiosError } from 'axios'
import { HttpClient } from '../lib/http/HttpClient'
import type { Book, BookDetail } from '../models/book'
import type { Course, KnowledgeArea, LiteraryGenre } from '../models/taxonomy'
import {
  list,
  parseArea,
  parseBookDetail,
  parseBookPage,
  parseCourse,
  parseGenre,
  type BookPage,
} from './catalog-parsers'

const http = new HttpClient().instance

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

/** Parâmetros da busca no acervo. */
export interface BookSearchParams {
  /** Texto livre: título, autores, assuntos, sinopse. */
  query: string
  /** Restringe a estas áreas. */
  areaIds?: readonly string[]
  /** Áreas cujos livros vêm primeiro (as do visitante). */
  preferredAreaIds?: readonly string[]
  page?: number
  pageSize?: number
  /** Cancela a requisição, por exemplo quando o visitante continua digitando. */
  signal?: AbortSignal
}

/**
 * Busca no acervo, do mais ao menos relevante.
 *
 * @param params - Texto, filtros e página.
 * @returns Uma página de resultados com o total encontrado.
 */
export async function searchBooks(params: BookSearchParams): Promise<BookPage> {
  const { data } = await http.get<unknown>('/books', {
    params: {
      q: params.query,
      area: params.areaIds,
      preferArea: params.preferredAreaIds,
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
