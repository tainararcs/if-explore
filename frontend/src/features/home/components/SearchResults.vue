<!-- Resultados da busca em grade, com estado vazio e ação para limpar. -->
<template>
  <section
    class="search-results"
    aria-labelledby="search-results-title"
  >
    <h2
      id="search-results-title"
      class="search-results__title"
      aria-live="polite"
    >
      {{ t('home.search.results', { query }, books.length) }}
    </h2>

    <ul
      v-if="books.length > 0"
      class="search-results__grid"
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
      class="search-results__empty"
    >
      <span class="search-results__empty-icon">
        <IconSearch />
      </span>
      <p class="search-results__empty-title">
        {{ t('home.search.emptyTitle') }}
      </p>
      <p class="search-results__empty-text">
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

<style scoped>
.search-results__title {
  margin-bottom: var(--space-5);
  font-size: var(--text-h2);
}

.search-results__grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: var(--space-6) var(--space-4);
  margin: 0;
  padding: 0;
  list-style: none;
}

.search-results__empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  max-width: 420px;
  margin-inline: auto;
  padding-block: var(--space-7);
  text-align: center;
}

.search-results__empty-icon {
  display: grid;
  place-items: center;
  width: 56px;
  height: 56px;
  border-radius: 50%;
  background: var(--color-primary-soft);
  color: var(--color-primary);
}

.search-results__empty-title {
  font-family: var(--font-display);
  font-size: var(--text-h2);
  line-height: 1.2;
}

.search-results__empty-text {
  margin-bottom: var(--space-2);
  color: var(--color-text-muted);
}

@media (min-width: 600px) {
  .search-results__grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (min-width: 900px) {
  .search-results__grid {
    grid-template-columns: repeat(5, minmax(0, 1fr));
    gap: var(--space-7) var(--space-5);
  }
}

@media (min-width: 1200px) {
  .search-results__grid {
    grid-template-columns: repeat(6, minmax(0, 1fr));
  }
}
</style>
