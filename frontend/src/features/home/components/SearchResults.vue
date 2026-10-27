<!-- Resultados da busca em grade, com estado vazio e ação para limpar. -->
<template>
  <section
    aria-labelledby="search-results-title"
  >
    <h2
      id="search-results-title"
      class="mb-6 text-h2"
      aria-live="polite"
    >
      {{ t('home.search.results', { query }, books.length) }}
    </h2>

    <ul
      v-if="books.length > 0"
      class="m-0 grid list-none grid-cols-2 gap-x-4 gap-y-8 p-0 sm:grid-cols-3 md:grid-cols-5 md:gap-x-6 md:gap-y-12 lg:grid-cols-6"
    >
      <li
        v-for="book in books"
        :key="book.id"
      >
        <BookCard :book="book" />
      </li>
    </ul>

    <div
      v-else
      class="mx-auto flex max-w-[420px] flex-col items-center gap-3 py-12 text-center"
    >
      <span class="grid size-14 place-items-center rounded-[50%] bg-primary-soft text-primary">
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
import IconSearch from '../../../components/icons/IconSearch.vue'
import type { Book } from '../../../models/book'
import BookCard from './BookCard.vue'

interface Props {
  query: string
  books: Book[]
}

defineProps<Props>()

const emit = defineEmits<{
  clear: []
}>()

const { t } = useI18n()
</script>
