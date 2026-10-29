<!--
  Destaque da página do livro: capa (fixa ao rolar no desktop), título e
  disponibilidade. O slot recebe o restante do conteúdo, que fica na coluna de
  detalhes a partir de 900px. A faixa na cor da capa é desenhada pela página.
-->
<template>
  <div>
    <div class="container grid gap-6 pt-2 md:grid-cols-[240px_minmax(0,1fr)] md:gap-12 md:pt-6">
      <div class="book-hero__cover mx-auto w-36 md:mx-0 md:w-full">
        <BookCover :book="book" />
      </div>

      <div class="min-w-0">
        <div class="flex flex-col items-center gap-2 text-center md:items-start md:text-left">
          <p class="eyebrow">
            {{ eyebrow }}
          </p>
          <h1
            ref="heading"
            class="book-hero__title outline-none"
            tabindex="-1"
          >
            {{ book.title }}
          </h1>
          <p class="text-body text-text-muted">
            {{ book.authors.join(', ') }}
          </p>
          <AvailabilityBadge
            class="mt-1 self-center md:self-start"
            :book="book"
            detailed
          />
        </div>
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useTemplateRef } from 'vue'
import AvailabilityBadge from '../../../components/AvailabilityBadge.vue'
import BookCover from '../../../components/BookCover.vue'
import type { Book } from '../../../models/book'

interface Props {
  book: Book
  /** Linha acima do título, como "Área · ano". */
  eyebrow: string
}

defineProps<Props>()

const heading = useTemplateRef<HTMLHeadingElement>('heading')

defineExpose({
  /** Move o foco para o título, ao trocar de livro pela prateleira de relacionados. */
  focusHeading: () => heading.value?.focus(),
})
</script>

<style scoped>
.book-hero__title {
  font-size: var(--text-h1);
}

@media (min-width: 900px) {
  .book-hero__cover {
    position: sticky;
    top: calc(var(--header-height) + var(--space-6));
    align-self: start;
  }

  .book-hero__title {
    font-size: var(--text-display);
    line-height: 1.05;
  }
}
</style>
