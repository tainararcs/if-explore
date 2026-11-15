import axios from 'axios'
import { GOOGLE_BOOKS_API_KEY } from '../../../lib/env'

const VOLUMES_URL = 'https://www.googleapis.com/books/v1/volumes'
const EMBED_URL = 'https://books.google.com/books'
const VIEWABLE = new Set(['PARTIAL', 'ALL_PAGES'])
// Ids de volume do Google têm só letras, dígitos, "-" e "_".
const VOLUME_ID_PATTERN = /^[\w-]{1,64}$/

/** Prévia de leitura de um livro no Google Livros. */
export interface BookPreview {
  /** Endereço do leitor embutível do Google Livros, para um `<iframe>`. */
  embedUrl: string
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

// Devolve o id do volume quando ele tem páginas visíveis e pode ser embutido.
function previewVolumeId(item: unknown): string | null {
  if (!isRecord(item) || typeof item.id !== 'string' || !VOLUME_ID_PATTERN.test(item.id)) {
    return null
  }
  const { accessInfo } = item
  if (!isRecord(accessInfo) || accessInfo.embeddable !== true) {
    return null
  }
  return typeof accessInfo.viewability === 'string' && VIEWABLE.has(accessInfo.viewability) ? item.id : null
}

/**
 * Procura no Google Books uma prévia embutível do livro pelo ISBN.
 *
 * Faz uma requisição ao Google por chamada e nenhuma quando a chave não está
 * configurada. A resposta é validada aqui: só volumes com páginas visíveis e
 * embutíveis viram prévia.
 *
 * @param isbn - ISBN do livro, só com dígitos (e "X" no ISBN-10).
 * @param signal - Cancela a requisição quando o visitante troca de livro.
 * @returns A prévia, ou `null` sem chave, sem ISBN válido ou sem volume com prévia.
 * @throws Erros de rede ou HTTP do Axios (inclusive o cancelamento).
 */
export async function findBookPreview(isbn: string, signal?: AbortSignal): Promise<BookPreview | null> {
  const normalizedIsbn = isbn.replace(/[^\dX]/gi, '')
  if (!GOOGLE_BOOKS_API_KEY || (normalizedIsbn.length !== 10 && normalizedIsbn.length !== 13)) {
    return null
  }
  const { data } = await axios.get<unknown>(VOLUMES_URL, {
    params: {
      q: `isbn:${normalizedIsbn}`,
      fields: 'items(id,accessInfo(viewability,embeddable))',
      maxResults: 5,
      key: GOOGLE_BOOKS_API_KEY,
    },
    timeout: 10_000,
    signal,
  })
  if (!isRecord(data) || !Array.isArray(data.items)) {
    return null
  }
  for (const item of data.items) {
    const volumeId = previewVolumeId(item)
    if (volumeId) {
      // Sem `pg`, o Google mostra a página de detalhes do volume em vez de abrir o leitor.
      const params = new URLSearchParams({ id: volumeId, hl: 'pt-BR', pg: 'PP1', output: 'embed' })
      return { embedUrl: `${EMBED_URL}?${params.toString()}` }
    }
  }
  return null
}
