<!-- Sugestão da descoberta: card horizontal que leva ao livro, com capa, dados, disponibilidade e o motivo da IA. -->
<template>
  <RouterLink
    :to="`/books/${item.book.id}`"
    class="group grid grid-cols-[88px_minmax(0,1fr)] gap-4 rounded-md border border-border bg-surface p-3 text-text no-underline transition-[border-color] duration-(--duration-fast) ease-standard hover:border-border-strong hover:text-text sm:grid-cols-[104px_minmax(0,1fr)] sm:gap-5 sm:p-4"
  >
    <BookCover
      :book="item.book"
      decorative
    />
    <div class="flex min-w-0 flex-col gap-1">
      <h3 class="line-clamp-2 font-display text-h3 group-hover:underline">
        {{ item.book.title }}
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
    </div>
  </RouterLink>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import AvailabilityBadge from '../../../components/AvailabilityBadge.vue'
import BookCover from '../../../components/BookCover.vue'
import { formatAuthors } from '../../../lib/catalog-format'
import type { DiscoveryItem } from '../models/discovery'

interface Props {
  item: DiscoveryItem
}

defineProps<Props>()

const { t } = useI18n()
</script>
