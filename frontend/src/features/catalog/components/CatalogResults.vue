<!-- Resultados do catálogo em grade, com "mostrar mais", estado vazio e ação para limpar tudo. -->
<template>
  <section aria-labelledby="catalog-results-title">
    <h2
      id="catalog-results-title"
      class="sr-only"
      aria-live="polite"
    >
      {{ heading }}
    </h2>

    <template v-if="books.length > 0">
      <ul class="m-0 grid list-none grid-cols-2 gap-x-4 gap-y-8 p-0 sm:grid-cols-3 md:gap-x-6 md:gap-y-12 lg:grid-cols-4">
        <li
          v-for="book in books"
          :key="book.id"
        >
          <BookCard :book="book" />
        </li>
      </ul>

      <div
        v-if="canLoadMore || loadMoreFailed"
        class="mt-10 flex flex-col items-center gap-3"
      >
        <p
          v-if="loadMoreFailed"
          class="text-danger"
          role="alert"
        >
          {{ t('catalog.results.loadMoreError') }}
        </p>
        <button
          type="button"
          class="button button--secondary"
          :disabled="isLoadingMore"
          :aria-busy="isLoadingMore"
          @click="emit('loadMore')"
        >
          {{ isLoadingMore ? t('catalog.results.loadingMore') : t('catalog.results.loadMore') }}
        </button>
      </div>
    </template>

    <div
      v-else
      class="mx-auto flex max-w-[420px] flex-col items-center gap-3 py-12 text-center"
    >
      <span class="grid size-14 place-items-center rounded-[50%] bg-primary-soft text-on-primary-soft">
        <IconSearch />
      </span>
      <p class="font-display text-h2 leading-[1.2]">
        {{ t('catalog.results.emptyTitle') }}
      </p>
      <p class="mb-2 text-text-muted">
        {{ t('catalog.results.emptyText') }}
      </p>
      <button
        type="button"
        class="button button--secondary"
        @click="emit('clearAll')"
      >
        {{ t('catalog.results.clearAll') }}
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import BookCard from '../../../components/BookCard.vue'
import IconSearch from '../../../components/icons/IconSearch.vue'
import type { Book } from '../../../models/book'

interface Props {
  /** Texto buscado; vazio quando o catálogo só está filtrado. */
  query: string
  /** Livros já carregados, na ordem escolhida. */
  books: Book[]
  /** Total encontrado no acervo, que pode ser maior que os carregados. */
  total: number
  canLoadMore: boolean
  isLoadingMore: boolean
  loadMoreFailed: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  clearAll: []
  loadMore: []
}>()

const { t } = useI18n()
const numbers = new Intl.NumberFormat('pt-BR')

const heading = computed(() =>
  props.query
    ? t('catalog.results.countFor', { query: props.query, n: numbers.format(props.total) }, props.total)
    : t('catalog.results.count', { n: numbers.format(props.total) }, props.total),
)
</script>
