<!-- Card informativo de livro (não clicável nesta etapa): capa, título, autoria e disponibilidade. -->
<template>
  <article class="flex flex-col gap-3">
    <BookCover
      :book="book"
      decorative
    />
    <div class="flex min-w-0 flex-col gap-1">
      <h3 class="line-clamp-2 text-small sm:text-h3">
        {{ book.title }}
      </h3>
      <p class="truncate text-caption text-text-muted sm:text-small">
        {{ book.authors.join(', ') }}
      </p>
      <!-- Selo com ponto + texto: o estado não depende só da cor. -->
      <p
        class="mt-1 inline-flex items-center gap-1 self-start rounded-pill bg-surface-muted px-2 py-0.5 text-caption font-semibold before:size-1.5 before:rounded-[50%] before:bg-current before:content-['']"
        :class="book.availability === 'available' ? 'text-success' : 'text-warning'"
      >
        {{ t(`home.availability.${book.availability}`) }}
      </p>
      <blockquote
        v-if="showQuote && book.quote"
        class="m-0 mt-2 line-clamp-3 font-display text-small leading-[1.4] text-text-muted italic"
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
