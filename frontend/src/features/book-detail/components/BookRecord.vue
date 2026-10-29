<!-- Ficha técnica do livro, com botão para copiar a localização na estante. -->
<template>
  <section aria-labelledby="book-record-title">
    <h2
      id="book-record-title"
      class="mb-4 text-h3 font-semibold font-body"
    >
      {{ t('bookDetail.record.title') }}
    </h2>
    <dl class="m-0 grid gap-x-8 gap-y-4 rounded-md border border-border bg-surface p-4 sm:grid-cols-2 sm:p-6">
      <div class="min-w-0 sm:col-span-2">
        <dt class="eyebrow">
          {{ t('bookDetail.record.location') }}
        </dt>
        <dd class="m-0 mt-1 flex flex-wrap items-center gap-x-3 gap-y-1">
          <span class="font-display text-h3">{{ book.callNumber }}</span>
          <button
            type="button"
            class="button button--ghost button--small"
            @click="copyLocation"
          >
            <IconCheck
              v-if="copyState === 'copied'"
              class="size-4"
            />
            {{ copyLabel }}
          </button>
          <span
            class="sr-only"
            aria-live="polite"
          >{{ copyState === 'idle' ? '' : copyLabel }}</span>
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
    </dl>
  </section>
</template>

<script setup lang="ts">
import { computed, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import IconCheck from '../../../components/icons/IconCheck.vue'
import type { Book } from '../../../models/book'

interface Props {
  book: Book
  areaName: string
  /** Ano já formatado (obras antigas aparecem como "c. 375 a.C."). */
  yearLabel: string
  /** Cursos do campus aos quais o livro é indicado. */
  courseNames: string[]
}

const props = defineProps<Props>()

const COPY_FEEDBACK_MS = 2000

const { t } = useI18n()
const numberFormat = new Intl.NumberFormat('pt-BR')

const copyState = ref<'idle' | 'copied' | 'failed'>('idle')
let resetTimer: number | undefined

const copyLabel = computed(() => {
  if (copyState.value === 'copied') {
    return t('bookDetail.record.copied')
  }
  return copyState.value === 'failed'
    ? t('bookDetail.record.copyFailed')
    : t('bookDetail.record.copy')
})

const items = computed(() => {
  const { book } = props
  const list = [
    {
      key: 'copies',
      value: t('bookDetail.record.copiesValue', {
        available: book.copies.available,
        total: book.copies.total,
      }),
    },
    {
      key: 'publisher',
      value: book.edition ? `${book.publisher}, ${book.edition}` : book.publisher,
    },
    { key: 'year', value: props.yearLabel },
    { key: 'pages', value: numberFormat.format(book.pages) },
    { key: 'area', value: props.areaName },
  ]
  if (book.isbn) {
    list.push({ key: 'isbn', value: book.isbn })
  }
  if (props.courseNames.length > 0) {
    list.push({
      key: 'courses',
      value: new Intl.ListFormat('pt-BR', { type: 'conjunction' }).format(props.courseNames),
    })
  }
  return list
})

async function copyLocation(): Promise<void> {
  window.clearTimeout(resetTimer)
  try {
    await navigator.clipboard.writeText(props.book.callNumber)
    copyState.value = 'copied'
  } catch {
    copyState.value = 'failed'
  }
  resetTimer = window.setTimeout(() => {
    copyState.value = 'idle'
  }, COPY_FEEDBACK_MS)
}

onUnmounted(() => window.clearTimeout(resetTimer))
</script>
