// Desaceleração cúbica: visualmente próxima do token `--ease-standard` em `index.css`.
const easeOutCubic = (progress: number) => 1 - (1 - progress) ** 3

/**
 * Anima a rolagem horizontal de um elemento até `left`, com duração fixa e a
 * mesma curva em qualquer navegador.
 *
 * @param element - Contêiner com rolagem horizontal.
 * @param left - Posição final de `scrollLeft`, em pixels.
 * @param duration - Duração da animação, em milissegundos.
 * @param onEnd - Chamada quando a animação termina ou é cancelada.
 * @returns Função que interrompe a animação na posição atual.
 */
export function animateScrollLeft(
  element: HTMLElement,
  left: number,
  duration: number,
  onEnd: () => void,
): () => void {
  const start = element.scrollLeft
  const distance = left - start
  const startedAt = performance.now()
  let frame = 0

  const tick = (now: number) => {
    const progress = Math.min((now - startedAt) / duration, 1)
    element.scrollLeft = start + distance * easeOutCubic(progress)
    if (progress < 1) {
      frame = requestAnimationFrame(tick)
    } else {
      onEnd()
    }
  }

  frame = requestAnimationFrame(tick)
  return () => {
    cancelAnimationFrame(frame)
    onEnd()
  }
}
