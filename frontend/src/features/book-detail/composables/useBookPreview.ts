import { isCancel } from 'axios'
import { onUnmounted, ref, watch, type Ref } from 'vue'
import { findBookPreview, type BookPreview } from '../services/google-books-service'

/**
 * Procura a prévia de leitura do livro no Google Books, sem atrasar a página.
 * Sem chave configurada, sem ISBN ou com qualquer falha, não há prévia. Ao
 * trocar de livro, a busca anterior é cancelada.
 *
 * @param isbn - ISBN do livro aberto; `null` enquanto carrega ou quando o catálogo não tem.
 * @returns A prévia encontrada, ou `null`.
 */
export function useBookPreview(isbn: Ref<string | null>) {
  const preview = ref<BookPreview | null>(null)

  let controller: AbortController | null = null

  async function load(value: string | null): Promise<void> {
    controller?.abort()
    controller = null
    preview.value = null
    if (!value) {
      return
    }
    const current = new AbortController()
    controller = current
    try {
      preview.value = await findBookPreview(value, current.signal)
    } catch (error) {
      if (!isCancel(error)) {
        preview.value = null
      }
    }
  }

  watch(isbn, (value) => void load(value), { immediate: true })

  onUnmounted(() => controller?.abort())

  return { preview }
}
