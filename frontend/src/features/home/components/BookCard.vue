<!-- Card informativo de livro (não clicável nesta etapa): capa, título, autoria e disponibilidade. -->
<template>
  <article class="book-card">
    <BookCover
      :book="book"
      decorative
    />
    <div class="book-card__body">
      <h3 class="book-card__title">
        {{ book.title }}
      </h3>
      <p class="book-card__author">
        {{ book.authors.join(', ') }}
      </p>
      <p
        class="book-card__status"
        :class="`book-card__status--${book.availability}`"
      >
        {{ t(`home.availability.${book.availability}`) }}
      </p>
      <blockquote
        v-if="showQuote && book.quote"
        class="book-card__quote"
      >
        “{{ book.quote }}”
      </blockquote>
    </div>
  </article>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import BookCover from '../../../components/BookCover.vue'
import type { Book } from '../../../models/book'

interface Props {
  book: Book
  /** Exibe a citação do livro, quando houver. */
  showQuote?: boolean
}

withDefaults(defineProps<Props>(), {
  showQuote: false,
})

const { t } = useI18n()
</script>

<style scoped>
.book-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.book-card__body {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  min-width: 0;
}

.book-card__title {
  font-size: var(--text-small);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.book-card__author {
  font-size: var(--text-caption);
  color: var(--color-text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Selo com ponto + texto: o estado não depende só da cor. */
.book-card__status {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  align-self: flex-start;
  margin-top: var(--space-1);
  padding: 2px var(--space-2);
  border-radius: var(--radius-pill);
  background: var(--color-surface-muted);
  font-size: var(--text-caption);
  font-weight: 600;
}

.book-card__status::before {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
}

.book-card__status--available {
  color: var(--color-success);
}

.book-card__status--borrowed {
  color: var(--color-warning);
}

.book-card__quote {
  display: -webkit-box;
  margin: var(--space-2) 0 0;
  font-family: var(--font-display);
  font-size: var(--text-small);
  font-style: italic;
  line-height: 1.4;
  color: var(--color-text-muted);
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

@media (min-width: 600px) {
  .book-card__title {
    font-size: var(--text-h3);
  }

  .book-card__author {
    font-size: var(--text-small);
  }
}
</style>
