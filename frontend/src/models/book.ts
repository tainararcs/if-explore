/** Situação de empréstimo de um exemplar no acervo. */
export type BookAvailability = 'available' | 'borrowed'

/**
 * Livro do acervo exibido pela aplicação.
 */
export interface Book {
  id: string
  title: string
  authors: string[]
  year: number
  /** Grande área do conhecimento principal do livro. */
  areaId: string
  courseIds: string[]
  genreIds: string[]
  subjects: string[]
  synopsis: string
  /** Trecho curto usado para despertar interesse; presente apenas em obras de domínio público. */
  quote?: string
  availability: BookAvailability
  /** Classificação e notação de autor usadas para localizar o livro na estante. */
  callNumber: string
}
