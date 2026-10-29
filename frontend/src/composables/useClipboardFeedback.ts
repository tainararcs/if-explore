import { onUnmounted, ref } from 'vue'

/** Resultado da última cópia; volta a `idle` após alguns segundos. */
export type CopyState = 'idle' | 'copied' | 'failed'

const FEEDBACK_MS = 2000

/**
 * Copia texto para a área de transferência e expõe um estado temporário para
 * o rótulo do botão ("Copiado", "Não foi possível copiar").
 *
 * @returns Estado atual e a função `copy`.
 */
export function useClipboardFeedback() {
  const state = ref<CopyState>('idle')
  let resetTimer: number | undefined

  async function copy(text: string): Promise<void> {
    window.clearTimeout(resetTimer)
    try {
      await navigator.clipboard.writeText(text)
      state.value = 'copied'
    } catch {
      state.value = 'failed'
    }
    resetTimer = window.setTimeout(() => {
      state.value = 'idle'
    }, FEEDBACK_MS)
  }

  onUnmounted(() => window.clearTimeout(resetTimer))

  return { state, copy }
}
