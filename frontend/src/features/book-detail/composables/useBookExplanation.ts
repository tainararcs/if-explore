import { isCancel } from 'axios'
import { onUnmounted, ref, watch, type Ref } from 'vue'
import { getBookExplanation } from '../services/book-detail-service'

/**
 * Carrega a explicação do livro gerada por IA, em paralelo com o livro e sem
 * atrasar a página. Uma falha apenas esconde a explicação. Ao trocar de livro,
 * o pedido anterior é cancelado.
 *
 * @param bookId - Id do livro vindo da rota.
 * @returns O texto (`null` quando não há) e se ainda está carregando.
 */
export function useBookExplanation(bookId: Ref<string>) {
  const text = ref<string | null>(null)
  const isLoading = ref(false)

  let controller: AbortController | null = null

  async function load(id: string): Promise<void> {
    controller?.abort()
    text.value = null
    if (!id) {
      isLoading.value = false
      return
    }
    const current = new AbortController()
    controller = current
    isLoading.value = true
    try {
      text.value = await getBookExplanation(id, current.signal)
    } catch (error) {
      if (isCancel(error)) {
        return
      }
      text.value = null
    }
    if (controller === current) {
      isLoading.value = false
    }
  }

  watch(bookId, (id) => void load(id), { immediate: true })

  onUnmounted(() => controller?.abort())

  return { text, isLoading }
}
