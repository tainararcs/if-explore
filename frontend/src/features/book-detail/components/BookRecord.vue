<!-- Ficha técnica do livro, com botão para copiar a localização na estante. Campos ausentes no catálogo não aparecem. -->
<template>
  <section aria-labelledby="book-record-title">
    <h2
      id="book-record-title"
      class="mb-4 text-h3 font-semibold font-body"
    >
      {{ t('bookDetail.record.title') }}
    </h2>
    <dl class="m-0 grid gap-x-8 gap-y-4 rounded-md border border-border bg-surface p-4 sm:grid-cols-2 sm:p-6">
      <div
        v-if="book.callNumber"
        class="min-w-0 sm:col-span-2"
      >
        <dt class="eyebrow">
          {{ t('bookDetail.record.location') }}
        </dt>
        <dd class="m-0 mt-1 flex flex-wrap items-center gap-x-3 gap-y-1">
          <span class="font-display text-h3">{{ book.callNumber }}</span>
          <CopyButton
            :text="book.callNumber"
            :label="t('bookDetail.record.copy')"
            :copied-label="t('bookDetail.record.copied')"
            :failed-label="t('bookDetail.record.copyFailed')"
          />
        </dd>
      </div>
      <div
        v-for="item in items"
        :key="item.key"
        class="min-w-0"
      >
        <dt class="eyebrow">
          {{ t(`bookDetail.record.${item.key}`) }}
        </dt>
        <dd class="m-0 mt-1">
          {{ item.value }}
        </dd>
      </div>
      <div
        v-if="book.links.length > 0"
        class="min-w-0 sm:col-span-2"
      >
        <dt class="eyebrow">
          {{ t('bookDetail.record.links') }}
        </dt>
        <dd class="m-0 mt-1">
          <ul class="m-0 flex list-none flex-wrap gap-x-6 gap-y-2 p-0">
            <li
              v-for="link in book.links"
              :key="link.url"
            >
              <ExternalLink :href="link.url">
                {{ link.label }}
              </ExternalLink>
            </li>
          </ul>
        </dd>
      </div>
    </dl>
  </section>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import CopyButton from '../../../components/CopyButton.vue'
import ExternalLink from '../../../components/ExternalLink.vue'
import type { BookCopies, BookDetail } from '../../../models/book'

interface Props {
  book: BookDetail
  /** Nome da área; vazio quando o livro não tem área. */
  areaName: string
  /** Cursos do campus aos quais o livro é indicado. */
  courseNames: string[]
}

const props = defineProps<Props>()

const { t } = useI18n()
const numberFormat = new Intl.NumberFormat('pt-BR')

const items = computed(() => {
  const { book } = props
  const candidates: { key: string; value: string | null }[] = [
    {
      key: 'copies',
      value: copiesText(book.copies),
    },
    {
      key: 'publisher',
      value: [book.publisher, book.edition].filter(Boolean).join(', ') || null,
    },
    { key: 'year', value: book.year === null ? null : String(book.year) },
    { key: 'pages', value: book.pages === null ? null : numberFormat.format(book.pages) },
    { key: 'area', value: props.areaName || null },
    { key: 'contributors', value: book.contributors },
    { key: 'isbn', value: book.isbn },
    {
      key: 'courses',
      value: props.courseNames.length > 0
        ? new Intl.ListFormat('pt-BR', { type: 'conjunction' }).format(props.courseNames)
        : null,
    },
  ]
  return candidates.filter((item): item is { key: string; value: string } => item.value !== null)
})

/** Contagem exata quando a consulta ao vivo a trouxe; senão, só o total. */
function copiesText(copies: BookCopies | null): string | null {
  if (copies === null || copies.total === 0) {
    return null
  }
  const { available, total } = copies
  return available === null
    ? t('bookDetail.record.copiesTotal', { n: total }, total)
    : t('bookDetail.record.copiesValue', { available, total })
}
</script>
