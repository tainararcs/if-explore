/** Exemplares do título no acervo, como verificados no catálogo da biblioteca. */
export interface BookCopies {
  total: number
  available: number
  /** Quando a situação foi consultada, em ISO 8601. */
  updatedAt: string
}

/**
 * Livro do acervo como aparece em listas, prateleiras e resultados de busca.
 * Campos ausentes no catálogo chegam como `null`.
 */
export interface Book {
  id: string
  title: string
  subtitle: string | null
  /** Como o catálogo grava ("SUMMERFIELD, Mark"); formate com `formatAuthorName` para exibir. */
  authors: string[]
  year: number | null
  /** Grande área do conhecimento; `null` em itens sem classificação (periódicos, CDs). */
  areaId: string | null
  courseIds: string[]
  genreIds: string[]
  /** Descritores do catálogo, em geral em maiúsculas; formate com `formatSubject` para exibir. */
  subjects: string[]
  synopsis: string | null
  /** Classificação e notação de autor usadas para localizar o livro na estante. */
  callNumber: string | null
  /** Só os dígitos. */
  isbn: string | null
  publisher: string | null
  edition: string | null
  pages: number | null
  /** Tipo como o catálogo exibe ("Livro", "Teses, dissertações, monografias, tcc"). */
  documentType: string | null
  coverUrl: string | null
  /** `null` enquanto os exemplares do título ainda não foram verificados. */
  copies: BookCopies | null
  /** Empréstimos já feitos, somando os exemplares. */
  loans: number
}

/** Arquivo digital do título: PDF do TCC ou e-book, termo de autorização, apresentação. */
export interface BookLink {
  label: string
  url: string
}

/** Livro completo, para a página do título. */
export interface BookDetail extends Book {
  /** Tradução, ilustração, orientação ("Trad. por: Fabiane Fiorini"). */
  contributors: string | null
  city: string | null
  country: string | null
  volume: string | null
  series: string | null
  physicalDescription: string | null
  issn: string | null
  issue: string | null
  languages: string[]
  notes: string[]
  links: BookLink[]
  /** Curso, só em TCCs ("Nutrição"). */
  tccCourse: string | null
  /** Data de entrada no catálogo, em ISO 8601. */
  catalogedAt: string | null
}

/** Situação para exibir: há exemplar livre, todos emprestados ou ainda não verificada. */
export type Availability = 'available' | 'borrowed' | 'unknown'

/**
 * Situação de disponibilidade de um livro.
 *
 * @param book - Livro avaliado.
 * @returns `unknown` quando os exemplares ainda não foram verificados.
 */
export function availabilityOf(book: Pick<Book, 'copies'>): Availability {
  if (book.copies === null) {
    return 'unknown'
  }
  return book.copies.available > 0 ? 'available' : 'borrowed'
}
