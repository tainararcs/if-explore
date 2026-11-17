const STORAGE_KEY = 'if-explore:home-shuffle-seed'

/** Maior semente aceita pela API (inteiro de 31 bits). */
const MAX_SHUFFLE_SEED = 2 ** 31 - 1

function isShuffleSeed(value: number): boolean {
  return Number.isInteger(value) && value >= 0 && value <= MAX_SHUFFLE_SEED
}

/**
 * Gera uma semente nova e a guarda para o restante da sessão.
 *
 * @returns A semente; ela vale para a tela mesmo se a gravação falhar.
 */
export function renewShuffleSeed(): number {
  const seed = Math.floor(Math.random() * (MAX_SHUFFLE_SEED + 1))
  try {
    window.sessionStorage.setItem(STORAGE_KEY, String(seed))
  } catch {
    // Armazenamento indisponível (modo privado, bloqueio): a semente vale só nesta tela.
  }
  return seed
}

/**
 * Semente do sorteio das prateleiras da home nesta sessão do navegador.
 *
 * A mesma semente dá as mesmas prateleiras: a home não muda quando o visitante
 * abre um livro e volta, mas muda numa visita nova. Valor ausente ou inválido
 * gera uma semente nova.
 *
 * @returns Inteiro entre 0 e 2³¹ − 1.
 */
export function loadShuffleSeed(): number {
  try {
    const seed = Number(window.sessionStorage.getItem(STORAGE_KEY) ?? Number.NaN)
    if (isShuffleSeed(seed)) {
      return seed
    }
  } catch {
    // Sem acesso ao armazenamento: segue com uma semente nova.
  }
  return renewShuffleSeed()
}
