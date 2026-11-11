<!--
  Sugestão da descoberta: card com capa, área e ano, título (link para o livro),
  autoria, disponibilidade, o motivo da IA e a localização na estante com botão
  para copiar. O título cobre o card inteiro como área de clique; o botão de
  copiar fica acima dele, para não haver um controle dentro de outro.
-->
<template>
  <article class="group relative grid h-full grid-cols-[88px_minmax(0,1fr)] gap-4 rounded-md border border-border bg-surface p-3 transition-[border-color] duration-(--duration-fast) ease-standard hover:border-border-strong sm:grid-cols-[104px_minmax(0,1fr)] sm:gap-5 sm:p-4">
    <BookCover
      class="self-start"
      :book="item.book"
      decorative
    />
    <div class="flex min-w-0 flex-col gap-1">
      <p
        v-if="meta"
        class="eyebrow m-0"
      >
        {{ meta }}
      </p>
      <h3 class="m-0 line-clamp-2 font-display text-h3">
        <RouterLink
          :to="`/books/${item.book.id}`"
          class="text-text no-underline after:absolute after:inset-0 after:rounded-md group-hover:underline hover:text-text"
        >
          {{ item.book.title }}
        </RouterLink>
      </h3>
      <p
        v-if="item.book.authors.length > 0"
        class="m-0 truncate text-small text-text-muted"
      >
        {{ formatAuthors(item.book.authors) }}
      </p>
      <AvailabilityBadge
        class="mt-1"
        :book="item.book"
        compact
      />
      <div
        v-if="item.reason"
        class="mt-3"
      >
        <p class="eyebrow m-0 text-primary">
          {{ t('discovery.reasonLabel') }}
        </p>
        <p class="m-0 mt-1 max-w-[65ch] text-small">
          {{ item.reason }}
        </p>
      </div>
      <div
        v-if="item.book.callNumber"
        class="relative z-10 mt-auto flex flex-wrap items-center gap-x-2 pt-3"
      >
        <span class="text-caption text-text-muted">{{ t('discovery.location') }}</span>
        <span class="font-display text-body">{{ item.book.callNumber }}</span>
        <button
          type="button"
          class="button button--ghost button--small -ms-1 min-h-11 px-2"
          :aria-label="copyState === 'idle' ? t('discovery.copyLocation', { title: item.book.title }) : copyLabel"
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
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AvailabilityBadge from '../../../components/AvailabilityBadge.vue'
import BookCover from '../../../components/BookCover.vue'
import IconCheck from '../../../components/icons/IconCheck.vue'
import { useClipboardFeedback } from '../../../composables/useClipboardFeedback'
import { formatAuthors } from '../../../lib/catalog-format'
import type { DiscoveryItem } from '../models/discovery'

interface Props {
  item: DiscoveryItem
  /** Nome da área do livro, quando conhecido. */
  areaName?: string
}

const props = withDefaults(defineProps<Props>(), {
  areaName: '',
})

const { t } = useI18n()
const { state: copyState, copy } = useClipboardFeedback()

const meta = computed(() =>
  [props.areaName, props.item.book.year ?? null].filter((part) => part !== null && part !== '').join(' · '),
)

const copyLabel = computed(() => {
  if (copyState.value === 'copied') {
    return t('discovery.copied')
  }
  return copyState.value === 'failed' ? t('discovery.copyFailed') : t('discovery.copy')
})

function copyLocation(): void {
  if (props.item.book.callNumber) {
    void copy(props.item.book.callNumber)
  }
}
</script>
