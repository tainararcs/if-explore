<!-- Atalhos para começar um pedido: os pedidos recentes do visitante (repetem o pedido) e ideias prontas (preenchem o campo). -->
<template>
  <div class="flex flex-col gap-6">
    <section
      v-if="recent.length > 0"
      :aria-labelledby="recentId"
    >
      <div class="mb-2 flex items-center justify-between gap-2">
        <h2
          :id="recentId"
          class="m-0 font-body text-small font-semibold text-text-muted"
        >
          {{ t('discovery.recent.title') }}
        </h2>
        <button
          type="button"
          class="button button--ghost button--small px-3"
          @click="emit('clearRecent')"
        >
          {{ t('discovery.recent.clear') }}
        </button>
      </div>
      <ul class="m-0 flex list-none flex-col gap-1 p-0">
        <li
          v-for="request in recent"
          :key="request"
        >
          <button
            type="button"
            class="flex min-h-11 w-full cursor-pointer items-center gap-3 rounded-md border-0 bg-transparent px-2 text-left text-small text-text hover:bg-surface-muted"
            :aria-label="t('discovery.recent.repeat', { request })"
            @click="emit('repeat', request)"
          >
            <IconHistory class="size-5 shrink-0 text-text-muted" />
            <span class="line-clamp-2">{{ request }}</span>
          </button>
        </li>
      </ul>
    </section>

    <section :aria-labelledby="ideasId">
      <h2
        :id="ideasId"
        class="m-0 mb-2 font-body text-small font-semibold text-text-muted"
      >
        {{ t('discovery.ideasLabel') }}
      </h2>
      <ul class="m-0 flex list-none flex-wrap gap-2 p-0">
        <li
          v-for="idea in ideas"
          :key="idea"
        >
          <button
            type="button"
            class="min-h-10 cursor-pointer rounded-pill border-[1.5px] border-chip-border bg-surface-muted px-3 text-left text-small font-medium text-text transition-[border-color] duration-(--duration-fast) ease-standard hover:border-border-strong"
            @click="emit('useIdea', idea)"
          >
            {{ idea }}
          </button>
        </li>
      </ul>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, useId } from 'vue'
import { useI18n } from 'vue-i18n'
import IconHistory from '../../../components/icons/IconHistory.vue'

interface Props {
  /** Pedidos recentes, do mais novo ao mais antigo. */
  recent: readonly string[]
}

defineProps<Props>()

const emit = defineEmits<{
  /** Refaz um pedido recente. */
  repeat: [request: string]
  /** Preenche o campo com uma ideia pronta, para o visitante ajustar antes de enviar. */
  useIdea: [idea: string]
  clearRecent: []
}>()

const { t } = useI18n()

const recentId = useId()
const ideasId = useId()

const IDEA_KEYS = ['light', 'programming', 'classics', 'health'] as const
const ideas = computed(() => IDEA_KEYS.map((key) => t(`discovery.ideas.${key}`)))
</script>
