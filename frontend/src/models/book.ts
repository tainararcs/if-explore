/** Valores aceitos em {@link BookCopies.status}. */
export const COPY_STATUSES = [
  'available',
  'in_library_use',
  'on_loan',
  'unavailable',
  'uncertain',
  'no_copies',
] as const

/**
 * Situação do título para quem procura o livro, calculada pela API:
 * - `available`: há exemplar livre para empréstimo;
 * - `in_library_use`: nenhum livre, mas há exemplar para ler na biblioteca;
 * - `on_loan`: nenhum livre; há exemplar emprestado ou reservado;
 * - `unavailable`: nenhum exemplar livre, emprestado ou para consulta;
 * - `uncertain`: a leitura em lote não permite saber se há exemplar livre;
 * - `no_copies`: o título não tem exemplar físico.
 */
export type CopyStatus = (typeof COPY_STATUSES)[number]

/** Exemplares do título no acervo, como lidos no catálogo da biblioteca. */
export interface BookCopies {
  total: number
  status: CopyStatus
  /** Exemplares livres; `null` quando a contagem exata não é conhecida (ela vem da consulta ao vivo da página do livro). */
  available: number | null
  /** Quando a situação foi lida, em ISO 8601. */
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
  /** `null` enquanto os exemplares do título ainda não foram lidos. */
  copies: BookCopies | null
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
  /** Empréstimos já feitos, somando os exemplares; `null` até a consulta ao vivo. */
  loans: number | null
}

/** Situação para exibir: a do título, ou `unknown` enquanto os exemplares não foram lidos. */
export type Availability = CopyStatus | 'unknown'

/**
 * Situação de disponibilidade de um livro.
 *
 * @param book - Livro avaliado.
 * @returns `unknown` quando os exemplares ainda não foram lidos.
 */
export function availabilityOf(book: Pick<Book, 'copies'>): Availability {
  return book.copies === null ? 'unknown' : book.copies.status
}
