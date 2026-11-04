import type { Book } from '../../../models/book'

/** Prateleiras de leituras relacionadas a um livro. */
export interface RelatedShelves {
  /** Autor compartilhado e seus outros livros; ausente com menos de dois. */
  sameAuthor: { author: string; books: Book[] } | null
  related: Book[]
}
