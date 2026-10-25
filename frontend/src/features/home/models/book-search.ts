import type { Book } from '../../../models/book'

/**
 * Normaliza texto para busca sem diferenciar maiúsculas nem acentos.
 *
 * @param value - Texto original.
 * @returns Texto em minúsculas e sem diacríticos.
 */
export function normalizeSearchText(value: string): string {
  return value.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().trim()
}

/**
 * Busca livros por título, autores e assuntos. Todos os termos da consulta
 * precisam aparecer. Livros das áreas do visitante vêm primeiro e, entre eles,
 * os que casam pelo título.
 *
 * @param books - Acervo pesquisado.
 * @param query - Texto digitado.
 * @param preferredAreaIds - Áreas do visitante, priorizadas no resultado.
 * @returns Livros encontrados, ordenados por relevância.
 */
export function searchBooks(
  books: readonly Book[],
  query: string,
  preferredAreaIds: readonly string[],
): Book[] {
  const terms = normalizeSearchText(query).split(/\s+/).filter(Boolean)
  if (terms.length === 0) {
    return []
  }

  return books
    .map((book) => {
      const title = normalizeSearchText(book.title)
      const haystack = normalizeSearchText(
        [book.title, ...book.authors, ...book.subjects].join(' '),
      )
      return {
        book,
        matches: terms.every((term) => haystack.includes(term)),
        rank:
          (preferredAreaIds.includes(book.areaId) ? 2 : 0) +
          (terms.every((term) => title.includes(term)) ? 1 : 0),
      }
    })
    .filter((entry) => entry.matches)
    .sort((a, b) => b.rank - a.rank || a.book.title.localeCompare(b.book.title, 'pt-BR'))
    .map((entry) => entry.book)
}
