import { API_BASE_URL } from './env'

/** Página inicial do catálogo oficial (PHL) da Biblioteca Roberval Cardoso. */
export const LIBRARY_CATALOG_URL =
  'https://biblioteca.barbacena.ifsudestemg.edu.br/cgi-bin/wxis.exe?IsisScript=phl82.xis&cipar=phl82.cip&lang=por'

/**
 * Link para a ficha de um livro no catálogo oficial.
 *
 * O PHL não tem endereço fixo por título (toda página depende de uma sessão
 * temporária), então o link aponta para a API, que abre a sessão na hora do
 * clique e redireciona para a ficha. Se o PHL falhar, a API leva à página
 * inicial do catálogo.
 *
 * @param bookId - Código do título no PHL.
 * @returns Endereço da rota de redirecionamento da API.
 */
export function libraryRecordUrl(bookId: string): string {
  return `${API_BASE_URL}/books/${encodeURIComponent(bookId)}/catalog`
}
