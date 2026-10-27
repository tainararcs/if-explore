<!--
  Prateleira horizontal de livros. No celular, rolagem livre por toque; a partir de
  900px, paginada de N em N livros, com setas e pontos indicando a página atual.
-->
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
      <div
        v-if="pageCount > 1"
        class="shelf__controls"
      >
        <button
          type="button"
          class="shelf__arrow"
          :aria-label="t('home.shelf.previous')"
          :disabled="currentPage === 0"
          @click="goToPage(currentPage - 1)"
        >
          <IconArrowLeft />
        </button>
        <button
          type="button"
          class="shelf__arrow"
          :aria-label="t('home.shelf.next')"
          :disabled="currentPage === pageCount - 1"
          @click="goToPage(currentPage + 1)"
        >
          <IconArrowRight />
        </button>
      </div>
    </div>

    <div
      ref="track"
      class="shelf__track"
      :class="{ 'shelf__track--animating': isAnimating }"
      role="region"
      tabindex="0"
      :aria-labelledby="headingId"
      @scroll.passive="updatePosition"
      @wheel.passive="stopAnimation"
      @pointerdown="stopAnimation"
    >
      <ul
        ref="list"
        class="shelf__list"
        :class="{ 'shelf__list--centered': pageCount === 1 }"
        :style="{ '--per-page': perPage }"
      >
        <li
          v-for="(book, index) in books"
          :key="book.id"
          class="shelf__item"
          :class="{ 'shelf__item--page-start': isPaged && index % perPage === 0 }"
        >
          <BookCard
            :book="book"
            :show-quote="showQuotes"
          />
        </li>
      </ul>
    </div>

    <div
      v-if="pageCount > 1"
      class="shelf__pagination"
      role="group"
      :aria-label="t('home.shelf.pages')"
    >
      <button
        v-for="page in pageCount"
        :key="page"
        type="button"
        class="shelf__dot"
        :aria-label="t('home.shelf.page', { current: page, total: pageCount })"
        :aria-current="page - 1 === currentPage ? 'true' : undefined"
        @click="goToPage(page - 1)"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, useId, useTemplateRef, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import IconArrowLeft from '../../../components/icons/IconArrowLeft.vue'
import IconArrowRight from '../../../components/icons/IconArrowRight.vue'
import { animateScrollLeft } from '../../../lib/animate-scroll'
import type { Book } from '../../../models/book'
import BookCard from './BookCard.vue'

interface Props {
  title: string
  books: Book[]
  /** Exibe as citações dos livros nos cards. */
  showQuotes?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showQuotes: false,
})

// Largura mínima de um card na versão paginada; define quantos cabem por página.
const MIN_ITEM_WIDTH = 150
const MIN_PER_PAGE = 2
const PAGED_QUERY = '(min-width: 900px)'
const PAGE_TRANSITION_MS = 450

const { t } = useI18n()
const headingId = useId()
const track = useTemplateRef<HTMLDivElement>('track')
const list = useTemplateRef<HTMLUListElement>('list')

const isPaged = ref(false)
const perPage = ref(MIN_PER_PAGE)
const gap = ref(0)
const currentPage = ref(0)
const isAnimating = ref(false)

const pageCount = computed(() =>
  isPaged.value ? Math.max(1, Math.ceil(props.books.length / perPage.value)) : 1,
)

// Distância entre o início de uma página e o da seguinte: a largura visível mais um gap.
function pageStride(element: HTMLElement): number {
  return element.clientWidth + gap.value
}

// Recalcula quantos livros cabem por página conforme a largura disponível.
function measure(): void {
  const element = track.value
  if (!element || !list.value) {
    return
  }
  isPaged.value = window.matchMedia(PAGED_QUERY).matches
  gap.value = Number.parseFloat(getComputedStyle(list.value).columnGap) || 0
  perPage.value = Math.max(
    MIN_PER_PAGE,
    Math.floor((element.clientWidth + gap.value) / (MIN_ITEM_WIDTH + gap.value)),
  )
  updatePosition()
}

// Deriva a página atual da rolagem; no fim da faixa, a última página fica ativa.
function updatePosition(): void {
  const element = track.value
  if (!element || !isPaged.value) {
    currentPage.value = 0
    return
  }
  const atEnd = element.scrollLeft + element.clientWidth >= element.scrollWidth - 1
  currentPage.value = atEnd
    ? pageCount.value - 1
    : Math.round(element.scrollLeft / pageStride(element))
}

let cancelAnimation: (() => void) | undefined

// Interrompe a troca de página animada, por exemplo quando o visitante rola por conta própria.
function stopAnimation(): void {
  cancelAnimation?.()
}

function goToPage(page: number): void {
  const element = track.value
  if (!element) {
    return
  }
  const target = Math.min(Math.max(page, 0), pageCount.value - 1)
  // Limita ao fim da faixa: a última página pode ter menos livros que as demais.
  const left = Math.min(target * pageStride(element), element.scrollWidth - element.clientWidth)

  stopAnimation()
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
    element.scrollLeft = left
    return
  }
  // O snap fica desligado durante a animação para não puxar a rolagem a cada quadro.
  isAnimating.value = true
  cancelAnimation = animateScrollLeft(element, left, PAGE_TRANSITION_MS, () => {
    isAnimating.value = false
    cancelAnimation = undefined
    updatePosition()
  })
}

// Filtrar a prateleira muda a quantidade de livros; a rolagem pode ter sido ajustada.
watch(() => props.books.length, updatePosition, { flush: 'post' })

const resizeObserver = new ResizeObserver(measure)

onMounted(() => {
  if (track.value) {
    resizeObserver.observe(track.value)
  }
  measure()
})

onUnmounted(() => {
  resizeObserver.disconnect()
  stopAnimation()
})
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

.shelf__pagination {
  display: none;
  justify-content: center;
  gap: var(--space-1);
  margin-top: var(--space-2);
}

/* Área de toque de 24px com o ponto visível menor no centro. */
.shelf__dot {
  display: grid;
  place-items: center;
  width: 24px;
  height: 24px;
  padding: 0;
  border: 0;
  background: none;
  cursor: pointer;
}

.shelf__dot::before {
  content: '';
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--color-border);
}

.shelf__dot:hover::before {
  background: var(--color-text-muted);
}

.shelf__dot[aria-current='true']::before {
  width: 20px;
  border-radius: var(--radius-pill);
  background: var(--color-primary);
}

@media (prefers-reduced-motion: no-preference) {
  .shelf__dot::before {
    transition:
      width var(--duration-base) var(--ease-standard),
      background-color var(--duration-base) var(--ease-standard);
  }
}

/*
  Versão paginada: cada página ocupa exatamente a largura visível, com
  `--per-page` livros (definido no script a partir da largura disponível).
*/
@media (min-width: 900px) {
  .shelf__controls,
  .shelf__pagination {
    display: flex;
  }

  .shelf__track {
    margin-inline: 0;
    padding-inline: 0;
    scroll-padding-inline: 0;
  }

  .shelf__list {
    gap: var(--space-5);
  }

  .shelf__list--centered {
    justify-content: center;
  }

  /* O snap só vale no início de cada página: gestos de rolagem param sempre numa página inteira. */
  .shelf__item {
    flex-basis: calc((100% - var(--space-5) * (var(--per-page) - 1)) / var(--per-page));
    scroll-snap-align: none;
  }

  .shelf__item--page-start {
    scroll-snap-align: start;
    scroll-snap-stop: always;
  }

  .shelf__track--animating {
    scroll-snap-type: none;
  }
}
</style>
