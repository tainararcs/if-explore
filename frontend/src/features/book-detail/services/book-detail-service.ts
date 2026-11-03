import { HttpClient } from '../../../lib/http/HttpClient'
import { list, parseBook, parseRecord, parseString } from '../../../services/catalog-parsers'
import type { RelatedShelves } from '../models/related-books'

const http = new HttpClient().instance

/**
 * Leituras relacionadas a um livro, calculadas pela API sobre o acervo inteiro.
 *
 * @param id - Identificador do livro aberto.
 * @returns Outros livros de um autor em comum (quando há ao menos dois) e os
 * demais por afinidade.
 */
export async function getRelatedBooks(id: string): Promise<RelatedShelves> {
  const { data } = await http.get<unknown>(`/books/${encodeURIComponent(id)}/related`)
  const body = parseRecord(data, 'related')
  let sameAuthor: RelatedShelves['sameAuthor'] = null
  if (body.sameAuthor !== null) {
    const author = parseRecord(body.sameAuthor, 'related.sameAuthor')
    sameAuthor = {
      author: parseString(author.author, 'related.sameAuthor.author'),
      books: list(author.books, 'related.sameAuthor.books', parseBook),
    }
  }
  return { sameAuthor, related: list(body.related, 'related.related', parseBook) }
}
