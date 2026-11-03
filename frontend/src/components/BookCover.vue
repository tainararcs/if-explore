<!--
  Capa do livro: a imagem do catálogo quando existe; senão, ou se a imagem falhar,
  uma capa tipográfica gerada no estilo de edição clássica.
-->
<template>
  <div
    class="book-cover"
    :style="{ '--cover-bg': coverColor }"
    :role="decorative ? undefined : 'img'"
    :aria-label="decorative ? undefined : label"
    :aria-hidden="decorative ? 'true' : undefined"
  >
    <img
      v-if="showImage"
      class="book-cover__image"
      :src="book.coverUrl ?? undefined"
      alt=""
      loading="lazy"
      decoding="async"
      @error="failedUrl = book.coverUrl"
    >
    <div
      v-else
      class="book-cover__face"
    >
      <span class="book-cover__author">{{ firstAuthor }}</span>
      <span class="book-cover__title">{{ book.title }}</span>
      <span class="book-cover__ornament" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { formatAuthorName, formatAuthors } from '../lib/catalog-format'
import { pickCoverColor } from '../lib/cover-color'
import type { Book } from '../models/book'

interface Props {
  book: Pick<Book, 'id' | 'title' | 'authors' | 'coverUrl'>
  /** Oculta a capa de leitores de tela quando o título já aparece em texto ao lado. */
  decorative?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  decorative: false,
})

const { t } = useI18n()

// Guarda a URL que falhou: se o livro mudar, a nova capa é tentada normalmente.
const failedUrl = ref<string | null>(null)
const showImage = computed(() => props.book.coverUrl !== null && props.book.coverUrl !== failedUrl.value)

const coverColor = computed(() => pickCoverColor(props.book.id))
const firstAuthor = computed(() => {
  const [author] = props.book.authors
  return author === undefined ? '' : formatAuthorName(author)
})
const label = computed(() =>
  t('common.coverLabel', { title: props.book.title, author: formatAuthors(props.book.authors) }),
)
</script>

<style scoped>
.book-cover {
  container-type: inline-size;
  position: relative;
  width: 100%;
  aspect-ratio: 2 / 3;
  border-radius: var(--radius-cover);
  background:
    linear-gradient(
      90deg,
      rgb(0 0 0 / 0.24) 0 6%,
      rgb(255 255 255 / 0.08) 6% 7.5%,
      transparent 7.5%
    ),
    var(--cover-bg);
  box-shadow: var(--shadow-md);
  color: #f6f2e9;
  overflow: hidden;
}

.book-cover__image {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
}

/* Filete interno, como nas capas de edições clássicas (só na capa gerada). */
.book-cover:not(:has(.book-cover__image))::after {
  content: '';
  position: absolute;
  inset: 6px 6px 6px calc(7.5% + 6px);
  border: 1px solid rgb(246 242 233 / 0.35);
  border-radius: 2px;
  pointer-events: none;
}

.book-cover__face {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: space-between;
  gap: 6cqi;
  height: 100%;
  padding: 14cqi 11cqi 13cqi calc(7.5% + 11cqi);
  text-align: center;
}

.book-cover__author {
  font-family: var(--font-body);
  font-size: max(6cqi, 0.5rem);
  font-weight: 600;
  letter-spacing: 0.12em;
  line-height: 1.3;
  text-transform: uppercase;
  opacity: 0.85;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.book-cover__title {
  font-family: var(--font-display);
  font-size: max(11cqi, 0.75rem);
  line-height: 1.15;
  overflow-wrap: anywhere;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.book-cover__ornament {
  position: relative;
  width: 24cqi;
  height: 1px;
  background: currentColor;
  opacity: 0.6;
}

.book-cover__ornament::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 5cqi;
  height: 5cqi;
  border: 1px solid currentColor;
  background: var(--cover-bg);
  transform: translate(-50%, -50%) rotate(45deg);
}
</style>
