// Tons profundos de biblioteca clássica, iguais nos temas claro e escuro.
const COVER_COLORS = [
  '#174D3B',
  '#356B56',
  '#2E5A6B',
  '#6E2F3A',
  '#8A4B1F',
  '#3E3A5C',
  '#5C5A2E',
  '#242722',
]

/**
 * Escolhe a cor da capa gerada a partir de um hash estável do id, para que o
 * livro tenha sempre a mesma cor na capa e no destaque da página do livro.
 *
 * @param id - Identificador do livro.
 * @returns Cor hexadecimal da paleta de capas.
 */
export function pickCoverColor(id: string): string {
  let hash = 0
  for (const char of id) {
    hash = (hash * 31 + char.charCodeAt(0)) >>> 0
  }
  return COVER_COLORS[hash % COVER_COLORS.length] ?? '#174D3B'
}
