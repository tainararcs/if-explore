<!-- Resultados da busca em grade, com "mostrar mais", estado vazio e ação para limpar. -->
<template>
  <section
    aria-labelledby="search-results-title"
  >
    <h2
      id="search-results-title"
      class="mb-6 text-h2"
      aria-live="polite"
    >
      {{ t('home.search.results', { query }, total) }}
    </h2>

    <template v-if="books.length > 0">
      <ul class="m-0 grid list-none grid-cols-2 gap-x-4 gap-y-8 p-0 sm:grid-cols-3 md:grid-cols-5 md:gap-x-6 md:gap-y-12 lg:grid-cols-6">
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
          {{ t('home.search.loadMoreError') }}
        </p>
        <button
          type="button"
          class="button button--secondary"
          :disabled="isLoadingMore"
          :aria-busy="isLoadingMore"
          @click="emit('loadMore')"
        >
          {{ isLoadingMore ? t('home.search.loadingMore') : t('home.search.loadMore') }}
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
        {{ t('home.search.emptyTitle') }}
      </p>
      <p class="mb-2 text-text-muted">
        {{ t('home.search.emptyText') }}
      </p>
      <button
        type="button"
        class="button button--secondary"
        @click="emit('clear')"
      >
        {{ t('home.search.clearAction') }}
      </button>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import BookCard from '../../../components/BookCard.vue'
import IconSearch from '../../../components/icons/IconSearch.vue'
import type { Book } from '../../../models/book'

interface Props {
  query: string
  /** Resultados já carregados, na ordem de relevância. */
  books: Book[]
  /** Total encontrado no acervo, que pode ser maior que os carregados. */
  total: number
  canLoadMore: boolean
  isLoadingMore: boolean
  loadMoreFailed: boolean
}

defineProps<Props>()

const emit = defineEmits<{
  clear: []
  loadMore: []
}>()

const { t } = useI18n()
</script>
