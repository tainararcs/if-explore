<!--
  Atalhos discretos abaixo do formulário: ideias prontas em uma linha de links
  (preenchem o campo) e os pedidos recentes recolhidos num "Pedidos recentes (n)"
  que só abre quando o visitante quer (repetem o pedido).
-->
<template>
  <div class="flex flex-col gap-2 px-1 text-caption text-text-muted">
    <p
      :id="ideasId"
      class="m-0"
    >
      {{ t('discovery.ideasLabel') }}
    </p>
    <ul
      class="m-0 -mt-1 flex list-none flex-wrap gap-x-3 p-0"
      :aria-labelledby="ideasId"
    >
      <li
        v-for="idea in ideas"
        :key="idea"
      >
        <button
          type="button"
          class="min-h-8 cursor-pointer border-0 bg-transparent p-0 text-left font-medium text-primary underline decoration-primary/40 underline-offset-2 hover:decoration-primary"
          @click="emit('useIdea', idea)"
        >
          {{ idea }}
        </button>
      </li>
    </ul>

    <details
      v-if="recent.length > 0"
      class="discovery-recent group"
    >
      <summary class="inline-flex min-h-8 cursor-pointer list-none items-center gap-1 font-medium hover:text-text">
        <IconHistory class="size-4 shrink-0" />
        {{ t('discovery.recent.title', { n: recent.length }) }}
        <IconChevronDown class="size-4 shrink-0 transition-transform duration-(--duration-fast) ease-standard group-open:rotate-180" />
      </summary>
      <ul class="m-0 mt-1 flex list-none flex-col p-0">
        <li
          v-for="request in recent"
          :key="request"
        >
          <button
            type="button"
            class="flex min-h-8 w-full cursor-pointer items-center rounded-sm border-0 bg-transparent px-1 text-left text-caption text-text hover:bg-surface-muted"
            :aria-label="t('discovery.recent.repeat', { request })"
            @click="emit('repeat', request)"
          >
            <span class="truncate">{{ request }}</span>
          </button>
        </li>
      </ul>
      <button
        type="button"
        class="mt-1 min-h-8 cursor-pointer border-0 bg-transparent p-0 text-caption font-medium text-text-muted underline underline-offset-2 hover:text-text"
        @click="emit('clearRecent')"
      >
        {{ t('discovery.recent.clear') }}
      </button>
    </details>
  </div>
</template>

<script setup lang="ts">
import { computed, useId } from 'vue'
import { useI18n } from 'vue-i18n'
import IconChevronDown from '../../../components/icons/IconChevronDown.vue'
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

const ideasId = useId()

const IDEA_KEYS = ['light', 'programming', 'classics', 'health'] as const
const ideas = computed(() => IDEA_KEYS.map((key) => t(`discovery.ideas.${key}`)))
</script>

<style scoped>
/* Esconde o triângulo padrão do <summary> no Safari; a seta é o ícone. */
.discovery-recent summary::-webkit-details-marker {
  display: none;
}
</style>
