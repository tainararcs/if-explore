import { isCancel } from 'axios'
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useReadingPreferences } from '../../../composables/useReadingPreferences'
import { isValidQuery, normalizeQuery, type DiscoveryResult } from '../models/discovery'
import { discover, RateLimitedError } from '../services/discovery-service'

/** Estado do pedido de sugestões. */
export type DiscoveryState =
  | { status: 'idle' }
  | { status: 'loading' }
  | { status: 'success'; result: DiscoveryResult }
  | { status: 'error'; rateLimited: boolean }

// Último resultado da sessão: voltar de um livro para a descoberta mostra as mesmas
// sugestões em vez de pedir de novo à IA (que gastaria cota e poderia mudar a lista).
let lastResult: { query: string; withProfile: boolean; result: DiscoveryResult } | null = null

function readQueryParam(value: unknown): string {
  return typeof value === 'string' ? value : ''
}

/**
 * Pedido de sugestões à IA com o texto sincronizado ao parâmetro `?q=` da URL:
 * um link com `q` faz o pedido ao abrir (ou reaproveita o último resultado,
 * quando é o mesmo pedido), e voltar pelo histórico refaz o pedido daquela
 * entrada. Um novo pedido cancela o anterior.
 *
 * @returns Texto digitado, opção de considerar as preferências, estado do
 * pedido e as ações `submit` e `retry`.
 */
export function useDiscovery() {
  const route = useRoute()
  const router = useRouter()
  const { preferences, hasPreferences } = useReadingPreferences()

  const input = ref(readQueryParam(route.query.q))
  const usePreferences = ref(true)
  const state = ref<DiscoveryState>({ status: 'idle' })
  // Pedido que gerou o estado atual, mostrado no título dos resultados.
  const submittedQuery = ref('')

  let controller: AbortController | null = null

  const canSubmit = computed(() => isValidQuery(input.value))
  const isLoading = computed(() => state.value.status === 'loading')

  async function run(query: string): Promise<void> {
    controller?.abort()
    controller = new AbortController()
    submittedQuery.value = query
    state.value = { status: 'loading' }
    const profile = hasPreferences.value && usePreferences.value ? preferences.value : null
    try {
      const result = await discover(query, profile, controller.signal)
      lastResult = { query, withProfile: profile !== null, result }
      state.value = { status: 'success', result }
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

  function retry(): void {
    if (submittedQuery.value) {
      void run(submittedQuery.value)
    }
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
    submittedQuery,
    canSubmit,
    isLoading,
    submit,
    retry,
  }
}
