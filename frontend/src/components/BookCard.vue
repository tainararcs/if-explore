<!-- Card de livro que leva à página do livro: capa com selo "Explorar", título, autoria e disponibilidade. -->
<template>
  <RouterLink
    :to="`/books/${book.id}`"
    class="group flex flex-col gap-3 rounded-sm text-text no-underline hover:text-text"
    :class="{ 'book-card--focused': focused }"
  >
    <div class="relative motion-safe:transition-transform motion-safe:duration-(--duration-fast) motion-safe:ease-standard motion-safe:group-hover:-translate-y-0.5">
      <BookCover
        :book="book"
        decorative
      />
      <!-- O card inteiro é o link; o selo apenas indica que há mais a ver. -->
      <span
        class="book-card__badge absolute top-2 right-2 flex h-7 items-center rounded-sm text-caption font-semibold shadow-md"
        aria-hidden="true"
      >
        <span class="book-card__label">
          <span class="min-w-0 overflow-hidden whitespace-nowrap">
            <span class="block ps-2">{{ t('common.exploreBook') }}</span>
          </span>
        </span>
        <span class="grid size-7 shrink-0 place-items-center">
          <IconArrowUpRight class="book-card__icon size-4" />
        </span>
      </span>
    </div>
    <!--
      Título e autoria reservam sempre a mesma altura (2 linhas e 1 linha), mesmo
      quando o texto é menor ou falta, para que os selos fiquem alinhados entre os cards.
    -->
    <div class="flex min-w-0 flex-col gap-1">
      <h3 class="line-clamp-2 min-h-[2lh] text-small group-hover:underline sm:text-h3">
        {{ book.title }}
      </h3>
      <p class="min-h-lh truncate text-caption text-text-muted sm:text-small">
        {{ formatAuthors(book.authors) }}
      </p>
      <AvailabilityBadge
        class="mt-1"
        :book="book"
        compact
      />
    </div>
  </RouterLink>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { formatAuthors } from '../lib/catalog-format'
import type { Book } from '../models/book'
import AvailabilityBadge from './AvailabilityBadge.vue'
import BookCover from './BookCover.vue'
import IconArrowUpRight from './icons/IconArrowUpRight.vue'

interface Props {
  book: Book
  /** Mantém o selo expandido, como no livro central da prateleira em destaque no celular. */
  focused?: boolean
}

withDefaults(defineProps<Props>(), {
  focused: false,
})

const { t } = useI18n()
</script>

<style scoped>
/* As capas são escuras nos dois temas, então o selo usa as cores fixas do texto delas. */
.book-card__badge {
  background-color: #f6f2e9;
  color: var(--palette-green-900);
}

/* Reserva a faixa superior da capa para o selo (8px de margem, 28px de altura e 4px de folga). */
.group :deep(.book-cover__face) {
  padding-top: 40px;
}

/* A coluna de 0fr a 1fr anima a largura real do texto, fazendo o selo crescer para a esquerda. */
.book-card__label {
  display: grid;
  grid-template-columns: 0fr;
}

.book-card--focused .book-card__label,
.group:focus-visible .book-card__label {
  grid-template-columns: 1fr;
}

.book-card--focused .book-card__icon,
.group:focus-visible .book-card__icon {
  transform: scale(1.15);
}

@media (hover: hover) {
  .group:hover .book-card__label {
    grid-template-columns: 1fr;
  }

  .group:hover .book-card__icon {
    transform: scale(1.15);
  }
}

@media (prefers-reduced-motion: no-preference) {
  .book-card__label {
    transition: grid-template-columns var(--duration-base) var(--ease-standard);
  }

  .book-card__icon {
    transition: transform var(--duration-base) var(--ease-standard);
  }
}
</style>
