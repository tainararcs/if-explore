<!--
  Prateleira horizontal de livros. No celular, rolagem livre por toque (ou um livro
  em destaque por vez, com `featured`); a partir de 900px, paginada de N em N
  livros, com setas e pontos indicando a página atual.
-->
<template>
  <section
    class="shelf"
    :class="{ 'shelf--featured': featured }"
    :aria-labelledby="headingId"
  >
    <div class="mb-4 flex items-end justify-between gap-4">
      <h2
        :id="headingId"
      >
        {{ title }}
      </h2>
      <div
        v-if="pageCount > 1"
        class="hidden gap-2 md:flex"
      >
        <button
          type="button"
          class="grid size-11 cursor-pointer place-items-center rounded-[50%] border border-border bg-surface p-0 text-text enabled:hover:border-primary enabled:hover:text-primary disabled:cursor-not-allowed disabled:opacity-40"
          :aria-label="t('common.shelf.previous')"
          :disabled="currentPage === 0"
          @click="goToPage(currentPage - 1)"
        >
          <IconArrowLeft class="size-5" />
        </button>
        <button
          type="button"
          class="grid size-11 cursor-pointer place-items-center rounded-[50%] border border-border bg-surface p-0 text-text enabled:hover:border-primary enabled:hover:text-primary disabled:cursor-not-allowed disabled:opacity-40"
          :aria-label="t('common.shelf.next')"
          :disabled="currentPage === pageCount - 1"
          @click="goToPage(currentPage + 1)"
        >
          <IconArrowRight class="size-5" />
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
          :class="{
            'shelf__item--page-start': isPaged && index % perPage === 0,
            'shelf__item--current': layout === 'featured' && index === currentPage,
          }"
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
      :aria-label="t('common.shelf.pages')"
    >
      <button
        v-for="page in pageCount"
        :key="page"
        type="button"
        class="shelf__dot"
        :aria-label="t('common.shelf.page', { current: page, total: pageCount })"
        :aria-current="page - 1 === currentPage ? 'true' : undefined"
        @click="goToPage(page - 1)"
      />
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, useId, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import IconArrowLeft from './icons/IconArrowLeft.vue'
import IconArrowRight from './icons/IconArrowRight.vue'
import { animateScrollLeft } from '../lib/animate-scroll'
import type { Book } from '../models/book'
import BookCard from './BookCard.vue'

interface Props {
  title: string
  books: Book[]
  /** Exibe as citações dos livros nos cards. */
  showQuotes?: boolean
  /**
   * No celular, destaca um livro por vez no centro, com os vizinhos em segundo
   * plano e um ponto por livro. No desktop, mantém a paginação comum.
   */
  featured?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showQuotes: false,
  featured: false,
})

/**
 * Modo de exibição conforme a largura: `paged` (desktop, N livros por página),
 * `featured` (celular, um livro em destaque) ou `free` (celular, rolagem livre).
 */
type ShelfLayout = 'paged' | 'featured' | 'free'

// Largura mínima de um card na versão paginada; define quantos cabem por página.
const MIN_ITEM_WIDTH = 150
const MIN_PER_PAGE = 2
const PAGED_QUERY = '(min-width: 900px)'
const PAGE_TRANSITION_MS = 450

const { t } = useI18n()
const headingId = useId()
const track = useTemplateRef<HTMLDivElement>('track')
const list = useTemplateRef<HTMLUListElement>('list')

const layout = ref<ShelfLayout>('free')
const perPage = ref(MIN_PER_PAGE)
const gap = ref(0)
const itemWidth = ref(0)
const currentPage = ref(0)
const isAnimating = ref(false)

const isPaged = computed(() => layout.value === 'paged')

// No destaque, cada livro é uma "página" própria.
const pageCount = computed(() => {
  if (layout.value === 'featured') {
    return props.books.length
  }
  return isPaged.value ? Math.max(1, Math.ceil(props.books.length / perPage.value)) : 1
})

// Distância entre o início de uma página e o da seguinte, incluindo o gap.
function pageStride(element: HTMLElement): number {
  const pageWidth = layout.value === 'featured' ? itemWidth.value : element.clientWidth
  return pageWidth + gap.value
}

// Recalcula o modo e quantos livros cabem por página conforme a largura disponível.
function measure(): void {
  const element = track.value
  if (!element || !list.value) {
    return
  }
  if (window.matchMedia(PAGED_QUERY).matches) {
    layout.value = 'paged'
  } else {
    layout.value = props.featured ? 'featured' : 'free'
  }
  gap.value = Number.parseFloat(getComputedStyle(list.value).columnGap) || 0
  // offsetWidth ignora a escala aplicada pelo destaque, ao contrário de getBoundingClientRect.
  const firstItem = list.value.firstElementChild
  itemWidth.value = firstItem instanceof HTMLElement ? firstItem.offsetWidth : 0
  perPage.value = Math.max(
    MIN_PER_PAGE,
    Math.floor((element.clientWidth + gap.value) / (MIN_ITEM_WIDTH + gap.value)),
  )
  updatePosition()
}

// Deriva a página atual da rolagem; no fim da faixa, a última página fica ativa.
function updatePosition(): void {
  const element = track.value
  if (!element || layout.value === 'free') {
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

/* O snap fica desligado durante a troca animada para não puxar a rolagem a cada quadro. */
.shelf__track--animating {
  scroll-snap-type: none;
}

/*
  Destaque no celular: um livro centralizado por vez, com o anterior e o próximo
  aparecendo nas bordas. O preenchimento lateral permite centralizar o primeiro
  e o último livro.
*/
@media (max-width: 899px) {
  .shelf--featured {
    --featured-width: min(62vw, 280px);
  }

  .shelf--featured .shelf__track {
    padding-inline: calc((100vw - var(--featured-width)) / 2);
    scroll-padding-inline: 0;
  }

  /*
    A lista acompanha a largura dos livros; sem isso eles transbordam dela e o
    preenchimento final da faixa não entra na rolagem, deixando o último livro
    fora do centro.
  */
  .shelf--featured .shelf__list {
    width: max-content;
  }

  .shelf--featured .shelf__item {
    flex-basis: var(--featured-width);
    scroll-snap-align: center;
    scroll-snap-stop: always;
  }

  /*
    `--shelf-focus` vai de 0 (vizinho) a 1 (livro no centro) e define a escala do
    card e a opacidade da capa; o texto não esmaece, para manter o contraste.
    O destaque estático vale em qualquer navegador e com movimento reduzido.
  */
  .shelf--featured .shelf__item {
    transform: scale(calc(0.88 + 0.12 * var(--shelf-focus)));
  }

  .shelf--featured .shelf__item :deep(.book-cover) {
    opacity: calc(0.55 + 0.45 * var(--shelf-focus));
  }

  .shelf--featured .shelf__item:not(.shelf__item--current) {
    --shelf-focus: 0;
  }

  /* 24px por ponto sem espaço extra: até 12 pontos cabem em 360px. */
  .shelf--featured .shelf__pagination {
    display: flex;
    gap: 0;
  }
}

/* Registrada para poder ser interpolada por transições e animações. */
@property --shelf-focus {
  syntax: '<number>';
  inherits: true;
  initial-value: 1;
}

/*
  Com movimento permitido, o destaque troca com uma transição curta e, onde há
  suporte a animações guiadas pela rolagem, acompanha o dedo de forma contínua.
*/
@media (max-width: 899px) and (prefers-reduced-motion: no-preference) {
  .shelf--featured .shelf__item {
    transition: --shelf-focus var(--duration-base) var(--ease-standard);
  }

  @supports (animation-timeline: view()) {
    .shelf--featured .shelf__item {
      animation: shelf-focus linear both;
      animation-timeline: view(inline);
    }
  }
}

@keyframes shelf-focus {
  0%,
  100% {
    --shelf-focus: 0;
  }

  50% {
    --shelf-focus: 1;
  }
}

/*
  Versão paginada: cada página ocupa exatamente a largura visível, com
  `--per-page` livros (definido no script a partir da largura disponível).
*/
@media (min-width: 900px) {
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
}
</style>
