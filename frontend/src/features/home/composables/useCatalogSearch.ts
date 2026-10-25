import { computed, onMounted, ref, watch, type Ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import type { Book } from '../../../models/book'
import { getBooks } from '../../../services/catalog-service'
import { searchBooks } from '../models/book-search'

const DEBOUNCE_MS = 250

function readQueryParam(value: unknown): string {
  return typeof value === 'string' ? value : ''
}

/**
 * Busca no acervo com o texto sincronizado ao parâmetro `?q=` da URL, para
 * que recarregar a página mantenha a pesquisa.
 *
 * @param preferredAreaIds - Áreas do visitante, priorizadas nos resultados.
 * @returns Texto digitado (`input`), consulta aplicada, resultados e ações.
 */
export function useCatalogSearch(preferredAreaIds: Ref<readonly string[]>) {
  const route = useRoute()
  const router = useRouter()

  const books = ref<Book[]>([])
  const status = ref<'loading' | 'ready' | 'error'>('loading')
  const input = ref(readQueryParam(route.query.q))
  const query = ref(input.value.trim())

  const isSearching = computed(() => query.value.length > 0)
  const results = computed(() => searchBooks(books.value, query.value, preferredAreaIds.value))

  function apply(value: string): void {
    query.value = value.trim()
    if (readQueryParam(route.query.q) !== query.value) {
      void router.replace({ query: { ...route.query, q: query.value || undefined } })
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

  function clear(): void {
    input.value = ''
    apply('')
  }

  async function load(): Promise<void> {
    status.value = 'loading'
    try {
      books.value = await getBooks()
      status.value = 'ready'
    } catch {
      status.value = 'error'
    }
  }

  onMounted(load)

  return {
    input,
    query,
    isSearching,
    results,
    status,
    clear,
    reload: load,
  }
}
