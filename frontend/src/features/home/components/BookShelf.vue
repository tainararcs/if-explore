<!-- Prateleira horizontal de livros com rolagem por toque/teclado e setas a partir de 900px. -->
<template>
  <section
    class="shelf"
    :aria-labelledby="headingId"
  >
    <div class="shelf__header">
      <h2
        :id="headingId"
        class="shelf__title"
      >
        {{ title }}
      </h2>
      <div class="shelf__controls">
        <button
          type="button"
          class="shelf__arrow"
          :aria-label="t('home.shelf.previous')"
          :disabled="atStart"
          @click="scrollByPage(-1)"
        >
          <IconArrowLeft />
        </button>
        <button
          type="button"
          class="shelf__arrow"
          :aria-label="t('home.shelf.next')"
          :disabled="atEnd"
          @click="scrollByPage(1)"
        >
          <IconArrowRight />
        </button>
      </div>
    </div>

    <div
      ref="track"
      class="shelf__track"
      role="region"
      tabindex="0"
      :aria-labelledby="headingId"
      @scroll.passive="updateEdges"
    >
      <ul class="shelf__list">
        <li
          v-for="book in books"
          :key="book.id"
          class="shelf__item"
        >
          <BookCard
            :book="book"
            :show-quote="showQuotes"
          />
        </li>
      </ul>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, useId, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import IconArrowLeft from '../../../components/icons/IconArrowLeft.vue'
import IconArrowRight from '../../../components/icons/IconArrowRight.vue'
import type { Book } from '../../../models/book'
import BookCard from './BookCard.vue'

interface Props {
  title: string
  books: Book[]
  /** Exibe as citações dos livros nos cards. */
  showQuotes?: boolean
}

withDefaults(defineProps<Props>(), {
  showQuotes: false,
})

const { t } = useI18n()
const headingId = useId()
const track = useTemplateRef<HTMLDivElement>('track')

const atStart = ref(true)
const atEnd = ref(false)

// Habilita/desabilita as setas conforme a posição da rolagem.
function updateEdges(): void {
  const element = track.value
  if (!element) {
    return
  }
  atStart.value = element.scrollLeft <= 1
  atEnd.value = element.scrollLeft + element.clientWidth >= element.scrollWidth - 1
}

function scrollByPage(direction: 1 | -1): void {
  const element = track.value
  if (!element) {
    return
  }
  const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  element.scrollBy({
    left: direction * element.clientWidth * 0.8,
    behavior: reduceMotion ? 'auto' : 'smooth',
  })
}

const resizeObserver = new ResizeObserver(updateEdges)

onMounted(() => {
  if (track.value) {
    resizeObserver.observe(track.value)
  }
  updateEdges()
})

onUnmounted(() => resizeObserver.disconnect())
</script>

<style scoped>
.shelf__header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--space-4);
  margin-bottom: var(--space-4);
}

.shelf__controls {
  display: none;
  gap: var(--space-2);
}

.shelf__arrow {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  padding: 0;
  border: 1px solid var(--color-border);
  border-radius: 50%;
  background: var(--color-surface);
  color: var(--color-text);
  cursor: pointer;
}

.shelf__arrow:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.shelf__arrow:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.shelf__arrow :deep(svg) {
  width: 20px;
  height: 20px;
}

/* No celular a faixa encosta nas bordas da tela para a próxima capa aparecer. */
.shelf__track {
  margin-inline: calc(var(--gutter) * -1);
  padding: var(--space-2) var(--gutter) var(--space-4);
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scroll-padding-inline: var(--gutter);
  overscroll-behavior-x: contain;
  scrollbar-width: none;
}

.shelf__track::-webkit-scrollbar {
  display: none;
}

.shelf__list {
  display: flex;
  gap: var(--space-4);
  margin: 0;
  padding: 0;
  list-style: none;
}

/* min-width: 0 evita que autorias longas (sem quebra) alarguem o card. */
.shelf__item {
  flex: 0 0 132px;
  min-width: 0;
  scroll-snap-align: start;
}

@media (min-width: 900px) {
  .shelf__controls {
    display: flex;
  }

  .shelf__track {
    margin-inline: 0;
    padding-inline: 0;
    scroll-padding-inline: 0;
    scrollbar-width: thin;
  }

  .shelf__track::-webkit-scrollbar {
    display: initial;
  }

  .shelf__list {
    gap: var(--space-5);
  }

  .shelf__item {
    flex-basis: 160px;
  }
}
</style>
