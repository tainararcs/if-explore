<!-- Resumo do pedido enviado, mostrado no celular no lugar do formulário para que as sugestões apareçam logo. -->
<template>
  <div class="flex items-start gap-3 rounded-lg border border-border bg-surface p-4">
    <div class="min-w-0 flex-1">
      <p class="eyebrow m-0">
        {{ t('discovery.summary.label') }}
      </p>
      <p class="m-0 mt-1 line-clamp-3 font-display text-h3">
        {{ query }}
      </p>
    </div>
    <button
      type="button"
      class="button button--secondary button--small shrink-0"
      @click="emit('edit')"
    >
      {{ t('discovery.summary.edit') }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

interface Props {
  query: string
}

defineProps<Props>()

const emit = defineEmits<{
  /** Abre o formulário completo para mudar o pedido. */
  edit: []
}>()

const { t } = useI18n()
</script>
