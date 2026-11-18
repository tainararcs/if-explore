<!--
  Sugestão da IA na home: a prateleira de onde o livro veio, capa, título (link
  para o livro), autoria, área e ano, disponibilidade, o motivo da IA e a
  localização na estante com botão para copiar. No celular tudo fica numa coluna
  (rótulo, capa, texto), para o texto usar a largura do card; a partir de 900px a
  capa vai para a esquerda. O título cobre o card inteiro como área de clique; o
  botão de copiar fica acima dele, para não haver um controle dentro de outro.
-->
<template>
  <article class="ai-card group relative grid h-full gap-x-5 gap-y-3 rounded-md border border-border bg-surface p-4 transition-[border-color] duration-(--duration-fast) ease-standard hover:border-border-strong">
    <p class="ai-card__kind eyebrow m-0 text-primary">
      {{ t(`home.ai.kinds.${item.kind}`) }}
    </p>
    <BookCover
      class="ai-card__cover self-start"
      :book="item.book"
      decorative
    />
    <div class="ai-card__body flex min-w-0 flex-col gap-1">
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
      <p
        v-if="meta"
        class="m-0 text-caption text-text-muted"
      >
        {{ meta }}
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
          {{ t('home.ai.reasonLabel') }}
        </p>
        <p class="m-0 mt-1 max-w-[65ch] text-small">
          {{ item.reason }}
        </p>
      </div>
      <div
        v-if="item.book.callNumber"
        class="relative z-10 mt-auto flex flex-wrap items-center gap-x-2 pt-3"
      >
        <span class="text-caption text-text-muted">{{ t('home.ai.location') }}</span>
        <span class="font-display text-body">{{ item.book.callNumber }}</span>
        <CopyButton
          class="-ms-1 px-2"
          :text="item.book.callNumber"
          :label="t('home.ai.copy')"
          :copied-label="t('home.ai.copied')"
          :failed-label="t('home.ai.copyFailed')"
          :accessible-label="t('home.ai.copyLocation', { title: item.book.title })"
        />
      </div>
    </div>
  </article>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import AvailabilityBadge from '../../../components/AvailabilityBadge.vue'
import BookCover from '../../../components/BookCover.vue'
import CopyButton from '../../../components/CopyButton.vue'
import { formatAuthors } from '../../../lib/catalog-format'
import type { AiSuggestion } from '../models/ai-suggestions'

interface Props {
  item: AiSuggestion
  /** Nome da área do livro, quando conhecido. */
  areaName?: string
}

const props = withDefaults(defineProps<Props>(), {
  areaName: '',
})

const { t } = useI18n()

const meta = computed(() =>
  [props.areaName, props.item.book.year ?? null].filter((part) => part !== null && part !== '').join(' · '),
)
</script>

<style scoped>
.ai-card {
  grid-template-areas:
    'kind'
    'cover'
    'body';
  grid-template-columns: minmax(0, 1fr);
}

.ai-card__kind {
  grid-area: kind;
}

.ai-card__cover {
  grid-area: cover;
  width: 120px;
}

.ai-card__body {
  grid-area: body;
}

@media (min-width: 900px) {
  .ai-card {
    grid-template-areas:
      'cover kind'
      'cover body';
    grid-template-columns: 104px minmax(0, 1fr);
    grid-template-rows: auto 1fr;
  }

  .ai-card__cover {
    width: auto;
  }
}
</style>
