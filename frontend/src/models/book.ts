/** Exemplares do título no acervo. */
export interface BookCopies {
  total: number
  available: number
}

/**
 * Livro do acervo exibido pela aplicação.
 */
export interface Book {
  id: string
  title: string
  authors: string[]
  /** Ano da obra; negativo para obras anteriores à era comum (ex.: -375). */
  year: number
  /** Grande área do conhecimento principal do livro. */
  areaId: string
  courseIds: string[]
  genreIds: string[]
  subjects: string[]
  synopsis: string
  /** Trecho curto usado para despertar interesse; presente apenas em obras de domínio público. */
  quote?: string
  /** Classificação e notação de autor usadas para localizar o livro na estante. */
  callNumber: string
  /** ISBN-13 de uma edição real; ausente quando não confirmado. */
  isbn?: string
  publisher: string
  /** Edição por extenso, como "3ª edição". */
  edition?: string
  pages: number
  copies: BookCopies
}

/**
 * Indica se há ao menos um exemplar disponível para empréstimo.
 *
 * @param book - Livro avaliado.
 * @returns `true` quando há exemplar na estante.
 */
export function isAvailable(book: Pick<Book, 'copies'>): boolean {
  return book.copies.available > 0
}
