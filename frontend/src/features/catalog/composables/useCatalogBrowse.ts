import { isCancel } from 'axios'
import { computed, onUnmounted, ref, shallowRef, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useReadingPreferences } from '../../../composables/useReadingPreferences'
import type { Book } from '../../../models/book'
import { searchBooks } from '../../../services/catalog-service'
import {
  clearedFilters,
  countActiveFilters,
  readCatalogState,
  writeCatalogState,
  type CatalogFacets,
  type CatalogState,
} from '../models/catalog-filters'
import { getCatalogFacets } from '../services/facets-service'

const DEBOUNCE_MS = 250
const PAGE_SIZE = 24

type LoadStatus = 'loading' | 'ready' | 'error'

/**
 * Listagem do catálogo completo com busca, filtros e ordem guardados na URL:
 * recarregar a página ou voltar de um livro mantém tudo como estava.
 *
 * A lista vem da API, 24 livros por vez; as contagens de cada filtro chegam numa
 * consulta à parte, para não atrasar os resultados. Cada nova consulta cancela a
 * anterior, para que uma resposta atrasada não substitua a mais recente. As áreas
 * do visitante, quando há preferências, vêm primeiro na ordem.
 *
 * @returns Filtros atuais, texto digitado, resultados, contagens e ações.
 */
export function useCatalogBrowse() {
  const route = useRoute()
  const router = useRouter()
  const { preferences } = useReadingPreferences()

  const state = computed(() => readCatalogState(route.query))
  const input = ref(state.value.query)
  const books = ref<Book[]>([])
  const total = ref(0)
  const status = ref<LoadStatus>('loading')
  const isLoadingMore = ref(false)
  const loadMoreFailed = ref(false)
  const facets = shallowRef<CatalogFacets | null>(null)

  let page = 1
  let listController: AbortController | null = null
  let facetsController: AbortController | null = null

  const activeFilterCount = computed(() => countActiveFilters(state.value))
  const canLoadMore = computed(() => status.value === 'ready' && books.value.length < total.value)
  const preferredAreaIds = computed(() => preferences.value?.areaIds ?? [])

  /** Aplica uma mudança de filtros ou de ordem, gravando-a na URL. */
  function update(changes: Partial<CatalogState>): void {
    void router.replace({ query: writeCatalogState({ ...state.value, ...changes }) })
  }

  function clearFilters(): void {
    update(clearedFilters(state.value))
  }

  function clearAll(): void {
    input.value = ''
    update({ ...clearedFilters(state.value), query: '' })
  }

  async function fetchPage(nextPage: number): Promise<void> {
    listController?.abort()
    listController = new AbortController()
    const response = await searchBooks({
      ...state.value,
      sort: state.value.sort ?? undefined,
      preferredAreaIds: preferredAreaIds.value,
      page: nextPage,
      pageSize: PAGE_SIZE,
      signal: listController.signal,
    })
    page = nextPage
    total.value = response.total
    books.value = nextPage === 1 ? response.items : [...books.value, ...response.items]
  }

  async function load(): Promise<void> {
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

  async function loadFacets(): Promise<void> {
    facetsController?.abort()
    facetsController = new AbortController()
    try {
      facets.value = await getCatalogFacets(state.value, facetsController.signal)
    } catch {
      // Sem contagens os filtros continuam funcionando, só sem os números.
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

  // Aplica o texto só depois de uma pausa na digitação.
  watch(input, (value, _previous, onCleanup) => {
    const timer = window.setTimeout(() => {
      if (value.trim() !== state.value.query) {
        update({ query: value.trim() })
      }
    }, DEBOUNCE_MS)
    onCleanup(() => window.clearTimeout(timer))
  })

  // Mantém o campo coerente quando a URL muda pelo histórico do navegador.
  watch(
    () => state.value.query,
    (value) => {
      if (value !== input.value.trim()) {
        input.value = value
      }
    },
  )

  // A URL é a fonte dos filtros: qualquer mudança nela recarrega lista e contagens.
  // Ao sair para outra tela a query muda também; ali não há o que carregar.
  const catalogPath = route.path
  watch(
    () => (route.path === catalogPath ? JSON.stringify(writeCatalogState(state.value)) : null),
    (key) => {
      if (key !== null) {
        void load()
        void loadFacets()
      }
    },
    { immediate: true },
  )

  onUnmounted(() => {
    listController?.abort()
    facetsController?.abort()
  })

  return {
    state,
    input,
    books,
    total,
    status,
    facets,
    activeFilterCount,
    canLoadMore,
    isLoadingMore,
    loadMoreFailed,
    update,
    clearFilters,
    clearAll,
    loadMore,
    reload: load,
  }
}
