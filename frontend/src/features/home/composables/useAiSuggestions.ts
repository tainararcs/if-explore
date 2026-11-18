import { isCancel } from 'axios'
import { computed, onMounted, onUnmounted, ref, type Ref } from 'vue'
import { useReadingPreferences } from '../../../composables/useReadingPreferences'
import { getBooksByIds } from '../../../services/catalog-service'
import { MAX_EXCLUDED, type AiSuggestion } from '../models/ai-suggestions'
import { getAiSuggestions, RateLimitedError } from '../services/ai-suggestions-service'
import { loadAiSuggestions, saveAiSuggestions } from '../services/ai-suggestions-storage'

type SuggestionStatus = 'idle' | 'loading' | 'ready' | 'error'

/**
 * Aviso sobre o último pedido que não trouxe uma prateleira nova: IA fora do ar
 * (a API respondeu com a seleção por regras, que repetiria as outras prateleiras),
 * acervo sem outras opções ou limite de pedidos.
 */
type SuggestionNotice = 'unavailable' | 'exhausted' | 'rateLimited'

/**
 * Prateleira de sugestões da IA na home, pedida pelo visitante com um botão.
 *
 * Cada pedido é uma chamada ao Gemini. A prateleira fica guardada na sessão:
 * voltar de um livro a mostra de novo sem nova chamada, e "outras sugestões" não
 * repete o que já foi sugerido nem o que está em "Escolhidos para você".
 *
 * @param shownIds - Livros já em destaque na home, que a IA não deve repetir.
 * @returns Estado, sugestões, mensagem da IA, aviso e as ações de pedir.
 */
export function useAiSuggestions(shownIds: Ref<readonly string[]>) {
  const { preferences } = useReadingPreferences()

  const status = ref<SuggestionStatus>('idle')
  const items = ref<AiSuggestion[]>([])
  const message = ref<string | null>(null)
  const notice = ref<SuggestionNotice | null>(null)
  const isLoadingMore = ref(false)
  let seenIds: string[] = []
  let controller: AbortController | null = null

  const hasSuggestions = computed(() => items.value.length > 0)

  function excluded(): string[] {
    // As já sugeridas vêm primeiro: são as que mais incomodariam se voltassem.
    return [...new Set([...seenIds, ...shownIds.value])].slice(0, MAX_EXCLUDED)
  }

  async function request(): Promise<void> {
    const profile = preferences.value
    if (!profile) {
      return
    }
    controller?.abort()
    controller = new AbortController()
    notice.value = null
    const keepCurrent = hasSuggestions.value
    if (keepCurrent) {
      isLoadingMore.value = true
    } else {
      status.value = 'loading'
    }
    try {
      const result = await getAiSuggestions(profile, excluded(), controller.signal)
      if (result.source === 'rules') {
        notice.value = 'unavailable'
      } else if (result.items.length === 0) {
        notice.value = 'exhausted'
      } else {
        items.value = result.items
        message.value = result.message
        seenIds = [...new Set([...result.items.map((item) => item.book.id), ...seenIds])]
        saveAiSuggestions(profile, {
          message: result.message,
          picks: result.items.map((item) => ({ id: item.book.id, reason: item.reason })),
          seenIds,
        })
      }
      status.value = hasSuggestions.value ? 'ready' : 'idle'
    } catch (error) {
      if (isCancel(error)) {
        return
      }
      if (error instanceof RateLimitedError) {
        notice.value = 'rateLimited'
        status.value = hasSuggestions.value ? 'ready' : 'idle'
      } else {
        status.value = keepCurrent ? 'ready' : 'error'
      }
    } finally {
      isLoadingMore.value = false
    }
  }

  /** Mostra de novo a prateleira guardada na sessão, recarregando os livros (1 requisição). */
  async function restore(): Promise<void> {
    const profile = preferences.value
    const stored = profile ? loadAiSuggestions(profile) : null
    if (!stored || stored.picks.length === 0) {
      return
    }
    seenIds = stored.seenIds
    status.value = 'loading'
    try {
      const books = new Map((await getBooksByIds(stored.picks.map((pick) => pick.id))).map((book) => [book.id, book]))
      items.value = stored.picks.flatMap((pick) => {
        const book = books.get(pick.id)
        return book ? [{ book, reason: pick.reason }] : []
      })
      message.value = stored.message
    } catch {
      // Sem os livros, a prateleira volta ao botão; nada se perde além da cópia guardada.
      items.value = []
    }
    status.value = hasSuggestions.value ? 'ready' : 'idle'
  }

  onMounted(restore)
  onUnmounted(() => controller?.abort())

  return {
    status,
    items,
    message,
    notice,
    isLoadingMore,
    request,
  }
}
