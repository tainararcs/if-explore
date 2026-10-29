<!-- Card de livro que leva à página do livro: capa, título, autoria e disponibilidade. -->
<template>
  <RouterLink
    :to="`/books/${book.id}`"
    class="group flex flex-col gap-3 rounded-sm text-text no-underline hover:text-text"
  >
    <div class="motion-safe:transition-transform motion-safe:duration-(--duration-fast) motion-safe:ease-standard motion-safe:group-hover:-translate-y-0.5">
      <BookCover
        :book="book"
        decorative
      />
    </div>
    <div class="flex min-w-0 flex-col gap-1">
      <h3 class="line-clamp-2 text-small group-hover:underline sm:text-h3">
        {{ book.title }}
      </h3>
      <p class="truncate text-caption text-text-muted sm:text-small">
        {{ book.authors.join(', ') }}
      </p>
      <AvailabilityBadge
        class="mt-1"
        :book="book"
      />
      <blockquote
        v-if="showQuote && book.quote"
        class="m-0 mt-2 line-clamp-3 font-display text-small leading-[1.4] text-text-muted italic"
      >
        “{{ book.quote }}”
      </blockquote>
    </div>
  </RouterLink>
</template>

<script setup lang="ts">
import type { Book } from '../models/book'
import AvailabilityBadge from './AvailabilityBadge.vue'
import BookCover from './BookCover.vue'

interface Props {
  book: Book
  /** Exibe a citação do livro, quando houver. */
  showQuote?: boolean
}

withDefaults(defineProps<Props>(), {
  showQuote: false,
})
</script>
