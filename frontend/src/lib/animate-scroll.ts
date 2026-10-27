/**
 * Cria uma função de easing equivalente a `cubic-bezier(x1, y1, x2, y2)` do CSS.
 *
 * Resolve o parâmetro da curva para o progresso no tempo por bisseção, o que é
 * estável para qualquer curva válida (x1 e x2 entre 0 e 1).
 */
function cubicBezier(x1: number, y1: number, x2: number, y2: number): (time: number) => number {
  const coordinate = (t: number, p1: number, p2: number) =>
    3 * (1 - t) ** 2 * t * p1 + 3 * (1 - t) * t ** 2 * p2 + t ** 3

  return (time) => {
    let low = 0
    let high = 1
    let t = time
    for (let step = 0; step < 20; step += 1) {
      const x = coordinate(t, x1, x2)
      if (Math.abs(x - time) < 1e-4) {
        break
      }
      if (x < time) {
        low = t
      } else {
        high = t
      }
      t = (low + high) / 2
    }
    return coordinate(t, y1, y2)
  }
}

// Mesma curva do token `--ease-standard` em `index.css`.
const easeStandard = cubicBezier(0.2, 0, 0, 1)

/**
 * Anima a rolagem horizontal de um elemento até `left`, com duração fixa e a
 * curva `--ease-standard`, independentemente do navegador.
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

  const finish = () => {
    cancelAnimationFrame(frame)
    onEnd()
  }

  const tick = (now: number) => {
    const progress = Math.min((now - startedAt) / duration, 1)
    element.scrollLeft = start + distance * easeStandard(progress)
    if (progress < 1) {
      frame = requestAnimationFrame(tick)
    } else {
      onEnd()
    }
  }

  frame = requestAnimationFrame(tick)
  return finish
}
