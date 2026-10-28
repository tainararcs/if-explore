import type { Book } from '../../../models/book'

const MAX_RELATED = 12

/** Prateleiras de leituras relacionadas a um livro. */
export interface RelatedShelves {
  /** Autor compartilhado e seus outros livros; ausente com menos de dois. */
  sameAuthor: { author: string; books: Book[] } | null
  related: Book[]
}

function countShared(a: readonly string[], b: readonly string[]): number {
  return a.filter((item) => b.includes(item)).length
}

/**
 * Pontua a afinidade entre dois livros.
 *
 * Peso: mesmo autor (3) > cada assunto em comum (2) > gênero em comum (1) >
 * mesma área (1).
 */
export function relatedScore(book: Book, current: Book): number {
  return (
    countShared(book.authors, current.authors) * 3 +
    countShared(book.subjects, current.subjects) * 2 +
    (countShared(book.genreIds, current.genreIds) > 0 ? 1 : 0) +
    (book.areaId === current.areaId ? 1 : 0)
  )
}

/**
 * Monta as prateleiras de relacionados: outros livros do mesmo autor (quando
 * há pelo menos dois) e os demais por afinidade, sem repetir o livro atual.
 *
 * @param books - Acervo completo.
 * @param current - Livro aberto.
 * @returns Prateleiras por autor e por afinidade.
 */
export function buildRelatedShelves(books: readonly Book[], current: Book): RelatedShelves {
  const ranked = books
    .filter((book) => book.id !== current.id)
    .map((book) => ({ book, score: relatedScore(book, current) }))
    .filter((entry) => entry.score > 0)
    .sort((a, b) => b.score - a.score)
    .map((entry) => entry.book)

  const author = current.authors.find(
    (name) => ranked.filter((book) => book.authors.includes(name)).length >= 2,
  )
  const authorBooks = author ? ranked.filter((book) => book.authors.includes(author)) : []

  return {
    sameAuthor: author ? { author, books: authorBooks.slice(0, MAX_RELATED) } : null,
    related: ranked.filter((book) => !authorBooks.includes(book)).slice(0, MAX_RELATED),
  }
}
