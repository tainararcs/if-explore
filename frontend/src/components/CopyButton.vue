<!--
  Botão que copia um texto (como a localização na estante): o rótulo muda para
  "copiado" ou "falhou" por alguns segundos e a mudança é anunciada a leitores
  de tela, sem toast.
-->
<template>
  <!-- Classes e atributos de quem usa o componente vão para o botão, não para o anúncio ao lado. -->
  <button
    v-bind="$attrs"
    type="button"
    class="button button--ghost button--small"
    :aria-label="copyState === 'idle' ? accessibleLabel : undefined"
    @click="copy(text)"
  >
    <IconCheck
      v-if="copyState === 'copied'"
      class="size-4"
    />
    {{ currentLabel }}
  </button>
  <span
    class="sr-only"
    aria-live="polite"
  >{{ copyState === 'idle' ? '' : currentLabel }}</span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useClipboardFeedback } from '../composables/useClipboardFeedback'
import IconCheck from './icons/IconCheck.vue'

interface Props {
  /** Texto copiado para a área de transferência. */
  text: string
  /** Rótulo do botão em repouso ("Copiar localização"). */
  label: string
  /** Rótulo depois de copiar ("Localização copiada"). */
  copiedLabel: string
  /** Rótulo quando a cópia falha. */
  failedLabel: string
  /**
   * Nome acessível em repouso, quando o rótulo visível não basta para saber o que
   * será copiado (vários botões na mesma tela). Deve começar pelo rótulo visível.
   */
  accessibleLabel?: string
}

const props = defineProps<Props>()

defineOptions({ inheritAttrs: false })

const { state: copyState, copy } = useClipboardFeedback()

const currentLabel = computed(() => {
  if (copyState.value === 'copied') {
    return props.copiedLabel
  }
  return copyState.value === 'failed' ? props.failedLabel : props.label
})
</script>
