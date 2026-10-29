import type { Book } from '../models/book'
import type { Course, KnowledgeArea, LiteraryGenre } from '../models/taxonomy'
import { books } from './mocks/book-data'
import { courses, knowledgeAreas, literaryGenres } from './mocks/taxonomy-data'

const MOCK_DELAY_MS = 300

// Simula a latência de rede para que os estados de carregamento sejam exercitados.
function respond<T>(data: T): Promise<T> {
  return new Promise((resolve) => {
    window.setTimeout(() => resolve(data), MOCK_DELAY_MS)
  })
}

/**
 * Acesso ao acervo. Nesta etapa usa apenas dados fictícios locais; nenhuma
 * requisição é feita ao catálogo real da biblioteca.
 */
export function getKnowledgeAreas(): Promise<KnowledgeArea[]> {
  return respond([...knowledgeAreas])
}

export function getCourses(): Promise<Course[]> {
  return respond([...courses])
}

export function getLiteraryGenres(): Promise<LiteraryGenre[]> {
  return respond([...literaryGenres])
}

export function getBooks(): Promise<Book[]> {
  return respond([...books])
}

/**
 * Busca um livro pelo identificador.
 *
 * @param id - Identificador do livro.
 * @returns O livro, ou `null` quando não existe no acervo.
 */
export function getBookById(id: string): Promise<Book | null> {
  return respond(books.find((book) => book.id === id) ?? null)
}

/**
 * Busca livros pelos identificadores, preservando a ordem recebida.
 *
 * @param ids - Identificadores dos livros.
 * @returns Livros encontrados; ids inexistentes são ignorados.
 */
export function getBooksByIds(ids: readonly string[]): Promise<Book[]> {
  const found = ids
    .map((id) => books.find((book) => book.id === id))
    .filter((book): book is Book => book !== undefined)
  return respond(found)
}
