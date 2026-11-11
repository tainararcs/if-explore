import { isCancel } from 'axios'
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useReadingPreferences } from '../../../composables/useReadingPreferences'
import {
  isValidQuery,
  MAX_EXCLUDED,
  normalizeQuery,
  type DiscoveryProfile,
  type DiscoveryResult,
} from '../models/discovery'
import { discover, RateLimitedError } from '../services/discovery-service'
import {
  addRecentRequest,
  clearRecentRequests,
  loadRecentRequests,
} from '../services/recent-requests-storage'

/** Estado do pedido de sugestões. */
export type DiscoveryState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; result: DiscoveryResult }
  | { status: 'error'; rateLimited: boolean }

/** Estado do pedido de outras sugestões para o mesmo texto. */
export type MoreStatus = 'idle' | 'loading' | 'exhausted' | 'error' | 'rateLimited'

interface CachedDiscovery {
  query: string
  withProfile: boolean
  result: DiscoveryResult
  moreStatus: MoreStatus
}

// Último resultado da sessão: voltar de um livro para a descoberta mostra as mesmas
// sugestões em vez de pedir de novo à IA (que gastaria cota e poderia mudar a lista).
let lastResult: CachedDiscovery | null = null

function readQueryParam(value: unknown): string {
  return typeof value === 'string' ? value : ''
}

/**
 * Pedido de sugestões à IA com o texto sincronizado ao parâmetro `?q=` da URL:
 * um link com `q` faz o pedido ao abrir (ou reaproveita o último resultado,
 * quando é o mesmo pedido), e voltar pelo histórico refaz o pedido daquela
 * entrada. Um novo pedido cancela o anterior.
 *
 * Também guarda os pedidos recentes no navegador e pede outras sugestões para
 * o mesmo texto, sem repetir os livros já mostrados.
 *
 * @returns Texto digitado, opção de considerar as preferências, estado do
 * pedido, pedidos recentes e as ações.
 */
export function useDiscovery() {
  const route = useRoute()
  const router = useRouter()
  const { preferences, hasPreferences } = useReadingPreferences()

  const input = ref(readQueryParam(route.query.q))
  const usePreferences = ref(true)
  const state = ref<DiscoveryState>({ status: 'idle' })
  const moreStatus = ref<MoreStatus>('idle')
  const recentRequests = ref<string[]>(loadRecentRequests())
  // Pedido que gerou o estado atual, mostrado no título dos resultados.
  const submittedQuery = ref('')

  let controller: AbortController | null = null
  // As outras sugestões seguem a escolha de preferências feita no pedido original.
  let submittedProfile: DiscoveryProfile | null = null

  const canSubmit = computed(() => isValidQuery(input.value))
  const isLoading = computed(() => state.value.status === 'loading')
  const shownIds = computed(() =>
    state.value.status === 'success' ? state.value.result.items.map((item) => item.book.id) : [],
  )
  // O botão continua visível (desabilitado) enquanto as outras sugestões chegam.
  const canLoadMore = computed(
    () => shownIds.value.length > 0 && shownIds.value.length < MAX_EXCLUDED && moreStatus.value !== 'exhausted',
  )

  function remember(result: DiscoveryResult): void {
    lastResult = {
      query: submittedQuery.value,
      withProfile: submittedProfile !== null,
      result,
      moreStatus: moreStatus.value,
    }
  }

  function startRequest(): AbortSignal {
    controller?.abort()
    controller = new AbortController()
    return controller.signal
  }

  async function run(query: string): Promise<void> {
    const signal = startRequest()
    submittedQuery.value = query
    submittedProfile = hasPreferences.value && usePreferences.value ? preferences.value : null
    state.value = { status: 'loading' }
    moreStatus.value = 'idle'
    try {
      const result = await discover(query, submittedProfile, [], signal)
      state.value = { status: 'success', result }
      remember(result)
      recentRequests.value = addRecentRequest(recentRequests.value, query)
    } catch (error) {
      if (!isCancel(error)) {
        state.value = { status: 'error', rateLimited: error instanceof RateLimitedError }
      }
    }
  }

  /** Envia o texto digitado e registra o pedido na URL. */
  function submit(): void {
    if (!canSubmit.value) {
      return
    }
    const query = normalizeQuery(input.value)
    input.value = query
    if (readQueryParam(route.query.q) !== query) {
      void router.replace({ query: { ...route.query, q: query } })
    }
    void run(query)
  }

  /** Repete um pedido recente (ou uma ideia pronta) sem precisar digitar. */
  function submitText(text: string): void {
    input.value = text
    submit()
  }

  function retry(): void {
    if (submittedQuery.value) {
      void run(submittedQuery.value)
    }
  }

  /** Pede outras sugestões para o mesmo texto e as acrescenta ao fim da lista. */
  async function loadMore(): Promise<void> {
    if (state.value.status !== 'success' || !canLoadMore.value || moreStatus.value === 'loading') {
      return
    }
    const current = state.value.result
    const signal = startRequest()
    moreStatus.value = 'loading'
    try {
      const next = await discover(submittedQuery.value, submittedProfile, shownIds.value, signal)
      if (next.items.length === 0) {
        moreStatus.value = 'exhausted'
        remember(current)
        return
      }
      // A origem passa a ser a do último lote: o aviso de seleção por regras vale para os novos livros.
      const merged: DiscoveryResult = { ...current, source: next.source, items: [...current.items, ...next.items] }
      state.value = { status: 'success', result: merged }
      moreStatus.value = 'idle'
      remember(merged)
    } catch (error) {
      if (!isCancel(error)) {
        moreStatus.value = error instanceof RateLimitedError ? 'rateLimited' : 'error'
      }
    }
  }

  function clearRecent(): void {
    clearRecentRequests()
    recentRequests.value = []
  }

  // Refaz o pedido quando a URL muda pelo histórico do navegador.
  watch(
    () => readQueryParam(route.query.q),
    (value) => {
      const query = normalizeQuery(value)
      if (query !== submittedQuery.value && isValidQuery(query)) {
        input.value = query
        void run(query)
      }
    },
  )

  onMounted(() => {
    const query = normalizeQuery(input.value)
    if (lastResult?.query === query) {
      submittedQuery.value = query
      usePreferences.value = lastResult.withProfile || !hasPreferences.value
      submittedProfile = lastResult.withProfile ? preferences.value : null
      moreStatus.value = lastResult.moreStatus === 'exhausted' ? 'exhausted' : 'idle'
      state.value = { status: 'success', result: lastResult.result }
    } else if (isValidQuery(query)) {
      submit()
    }
  })

  onUnmounted(() => controller?.abort())

  return {
    input,
    usePreferences,
    hasPreferences,
    state,
    moreStatus,
    recentRequests,
    submittedQuery,
    canSubmit,
    canLoadMore,
    isLoading,
    submit,
    submitText,
    retry,
    loadMore,
    clearRecent,
  }
}
