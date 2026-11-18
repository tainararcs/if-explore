<!--
  Prateleira especial da IA, em destaque no topo da home. Antes do pedido mostra o
  convite e o botão; depois, até seis livros com o motivo de cada escolha. No
  celular os cards rolam na horizontal; a partir de 900px ficam em grade.
-->
<template>
  <section
    class="rounded-lg border border-border bg-surface p-4 sm:p-6"
    aria-labelledby="ai-shelf-title"
  >
    <div class="flex flex-wrap items-start justify-between gap-3">
      <div class="min-w-0">
        <h2
          id="ai-shelf-title"
          class="m-0 flex items-center gap-2"
        >
          <IconSparkle
            class="size-6 shrink-0 text-primary"
            aria-hidden="true"
          />
          {{ t('home.ai.title') }}
        </h2>
        <p
          v-if="status === 'ready' && message"
          class="m-0 mt-2 max-w-[65ch] text-text-muted"
        >
          {{ message }}
        </p>
      </div>
      <button
        v-if="status === 'ready'"
        type="button"
        class="button button--secondary button--small"
        :disabled="isLoadingMore"
        :aria-busy="isLoadingMore"
        @click="emit('request')"
      >
        {{ isLoadingMore ? t('home.ai.loadingMore') : t('home.ai.more') }}
      </button>
    </div>

    <div
      v-if="status === 'idle'"
      class="mt-3 flex flex-col items-start gap-4"
    >
      <p class="m-0 max-w-[65ch]">
        {{ t('home.ai.lead') }}
      </p>
      <button
        type="button"
        class="button button--primary"
        @click="emit('request')"
      >
        <IconSparkle
          class="size-5"
          aria-hidden="true"
        />
        {{ t('home.ai.request') }}
      </button>
      <p class="m-0 max-w-[65ch] text-caption text-text-muted">
        {{ t('home.ai.privacy') }}
      </p>
    </div>

    <div
      v-else-if="status === 'loading'"
      class="mt-4"
      role="status"
    >
      <p class="m-0 mb-4 text-text-muted">
        {{ t('home.ai.loading') }}
      </p>
      <div
        class="flex gap-4 overflow-hidden md:grid md:grid-cols-2 lg:grid-cols-3"
        aria-hidden="true"
      >
        <span
          v-for="item in 3"
          :key="item"
          class="skeleton h-44 w-[min(85%,22rem)] shrink-0 rounded-md md:w-auto"
        />
      </div>
    </div>

    <div
      v-else-if="status === 'error'"
      class="mt-4"
      role="alert"
    >
      <p class="mb-4 text-danger">
        {{ t('home.ai.error') }}
      </p>
      <button
        type="button"
        class="button button--secondary"
        @click="emit('request')"
      >
        {{ t('home.ai.retry') }}
      </button>
    </div>

    <template v-else>
      <ul
        v-if="items.length > 0"
        class="ai-list m-0 mt-4 flex list-none gap-4 overflow-x-auto p-0 md:grid md:grid-cols-2 md:overflow-visible lg:grid-cols-3"
        tabindex="0"
        :aria-label="t('home.ai.listLabel')"
      >
        <li
          v-for="item in items"
          :key="item.book.id"
          class="w-[min(85%,22rem)] shrink-0 md:w-auto"
        >
          <AiSuggestionCard
            :item="item"
            :area-name="item.book.areaId ? areaNames.get(item.book.areaId) : undefined"
          />
        </li>
      </ul>
      <p
        v-else
        class="m-0 mt-4 text-text-muted"
      >
        {{ t('home.ai.emptyFilter') }}
      </p>
      <p class="m-0 mt-4 text-caption text-text-muted">
        {{ t('home.ai.note') }}
      </p>
    </template>

    <p
      v-if="notice"
      class="m-0 mt-4 text-small"
      role="status"
    >
      {{ t(`home.ai.${notice}`) }}
    </p>
  </section>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import IconSparkle from '../../../components/icons/IconSparkle.vue'
import type { AiSuggestion } from '../models/ai-suggestions'
import AiSuggestionCard from './AiSuggestionCard.vue'

interface Props {
  status: 'idle' | 'loading' | 'ready' | 'error'
  /** Sugestões a mostrar, já filtradas pela área escolhida na home. */
  items: AiSuggestion[]
  message: string | null
  /** Aviso do último pedido sem prateleira nova. */
  notice: 'unavailable' | 'exhausted' | 'rateLimited' | null
  isLoadingMore: boolean
  /** Nome de cada área pelo id, para o card. */
  areaNames: Map<string, string>
}

defineProps<Props>()

const emit = defineEmits<{
  request: []
}>()

const { t } = useI18n()
</script>

<style scoped>
.ai-list {
  scroll-snap-type: x mandatory;
  scrollbar-width: none;
}

.ai-list > li {
  scroll-snap-align: start;
}

@media (min-width: 900px) {
  .ai-list {
    scroll-snap-type: none;
  }
}
</style>
