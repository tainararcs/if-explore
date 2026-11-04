import { isCancel } from 'axios'
import { computed, onUnmounted, ref, watch, type Ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Book } from '../../../models/book'
import { searchBooks } from '../../../services/catalog-service'

const DEBOUNCE_MS = 250
const PAGE_SIZE = 24

type SearchStatus = 'idle' | 'loading' | 'ready' | 'error'

function readQueryParam(value: unknown): string {
  return typeof value === 'string' ? value : ''
}

/**
 * Busca no acervo com o texto sincronizado ao parâmetro `?q=` da URL, para que
 * recarregar a página mantenha a pesquisa.
 *
 * A busca roda na API, do mais ao menos relevante, 24 livros por vez. Cada nova
 * consulta cancela a anterior, para que uma resposta atrasada não substitua a
 * mais recente.
 *
 * @param preferredAreaIds - Áreas do visitante, priorizadas nos resultados.
 * @param areaFilter - Área escolhida no filtro da home, ou `null` para todas.
 * @returns Texto digitado (`input`), consulta aplicada, resultados e ações.
 */
export function useCatalogSearch(
  preferredAreaIds: Ref<readonly string[]>,
  areaFilter: Ref<string | null>,
) {
  const route = useRoute()
  const router = useRouter()

  const input = ref(readQueryParam(route.query.q))
  const query = ref(input.value.trim())
  const results = ref<Book[]>([])
  const total = ref(0)
  const status = ref<SearchStatus>('idle')
  const isLoadingMore = ref(false)
  const loadMoreFailed = ref(false)

  let page = 1
  let controller: AbortController | null = null

  const isSearching = computed(() => query.value.length > 0)
  const canLoadMore = computed(() => status.value === 'ready' && results.value.length < total.value)

  function apply(value: string): void {
    query.value = value.trim()
    if (readQueryParam(route.query.q) !== query.value) {
      void router.replace({ query: { ...route.query, q: query.value || undefined } })
    }
  }

  async function fetchPage(nextPage: number): Promise<void> {
    controller?.abort()
    controller = new AbortController()
    const response = await searchBooks({
      query: query.value,
      areaIds: areaFilter.value === null ? [] : [areaFilter.value],
      preferredAreaIds: preferredAreaIds.value,
      page: nextPage,
      pageSize: PAGE_SIZE,
      signal: controller.signal,
    })
    page = nextPage
    total.value = response.total
    results.value = nextPage === 1 ? response.items : [...results.value, ...response.items]
  }

  async function load(): Promise<void> {
    if (!isSearching.value) {
      controller?.abort()
      status.value = 'idle'
      results.value = []
      total.value = 0
      return
    }
    status.value = 'loading'
    loadMoreFailed.value = false
    try {
      await fetchPage(1)
      status.value = 'ready'
    } catch (error) {
      if (!isCancel(error)) {
        status.value = 'error'
      }
    }
  }

  /** Acrescenta a próxima página aos resultados. */
  async function loadMore(): Promise<void> {
    if (!canLoadMore.value || isLoadingMore.value) {
      return
    }
    isLoadingMore.value = true
    loadMoreFailed.value = false
    try {
      await fetchPage(page + 1)
    } catch (error) {
      if (!isCancel(error)) {
        loadMoreFailed.value = true
      }
    } finally {
      isLoadingMore.value = false
    }
  }

  // Aplica a consulta só depois de uma pausa na digitação.
  watch(input, (value, _previous, onCleanup) => {
    const timer = window.setTimeout(() => apply(value), DEBOUNCE_MS)
    onCleanup(() => window.clearTimeout(timer))
  })

  // Mantém o campo coerente quando a URL muda pelo histórico do navegador.
  watch(
    () => readQueryParam(route.query.q),
    (value) => {
      if (value !== query.value) {
        input.value = value
        query.value = value.trim()
      }
    },
  )

  watch([query, areaFilter, preferredAreaIds], () => void load(), { immediate: true })

  onUnmounted(() => controller?.abort())

  function clear(): void {
    input.value = ''
    apply('')
  }

  return {
    input,
    query,
    isSearching,
    results,
    total,
    status,
    canLoadMore,
    isLoadingMore,
    loadMoreFailed,
    clear,
    loadMore,
    reload: load,
  }
}
