import { HttpClient } from '../../../lib/http/HttpClient'
import { list, parseBook, parseNullableString, parseRecord, parseString } from '../../../services/catalog-parsers'
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

/**
 * Explicação simplificada do livro gerada por IA a partir da ficha, guardada
 * pela API depois da primeira vez.
 *
 * @param id - Identificador do livro aberto.
 * @param signal - Cancela a requisição quando o visitante troca de livro.
 * @returns O texto, ou `null` quando não há explicação (sem dados ou IA indisponível).
 */
export async function getBookExplanation(id: string, signal?: AbortSignal): Promise<string | null> {
  const { data } = await http.get<unknown>(`/books/${encodeURIComponent(id)}/explanation`, { signal })
  const body = parseRecord(data, 'explanation')
  const text = parseNullableString(body.text, 'explanation.text')
  return text?.trim() ? text : null
}
