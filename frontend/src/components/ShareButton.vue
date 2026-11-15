<!--
  Compartilha o link da página atual: usa o compartilhamento nativo quando o
  navegador oferece (celulares) e, nos demais casos, copia o link.
-->
<template>
  <!-- Classes e atributos de quem usa o componente vão para o botão, não para o anúncio ao lado. -->
  <button
    v-bind="$attrs"
    type="button"
    class="button"
    :class="small ? 'button--ghost button--small' : 'button--secondary'"
    @click="share"
  >
    <IconCheck
      v-if="copyState === 'copied'"
      class="size-5"
    />
    <IconShare
      v-else
      class="size-5"
    />
    {{ label }}
  </button>
  <span
    class="sr-only"
    aria-live="polite"
  >{{ copyState === 'idle' ? '' : label }}</span>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useClipboardFeedback } from '../composables/useClipboardFeedback'
import IconCheck from './icons/IconCheck.vue'
import IconShare from './icons/IconShare.vue'

interface Props {
  /** Título enviado ao compartilhamento nativo. */
  title: string
  /** Texto que acompanha o link no compartilhamento nativo. */
  text: string
  /** Versão discreta (botão fantasma pequeno), para ações secundárias. */
  small?: boolean
}

defineOptions({ inheritAttrs: false })

const props = withDefaults(defineProps<Props>(), {
  small: false,
})

const { t } = useI18n()
const { state: copyState, copy } = useClipboardFeedback()

const label = computed(() => {
  if (copyState.value === 'copied') {
    return t('common.share.copied')
  }
  return copyState.value === 'failed' ? t('common.share.failed') : t('common.share.action')
})

async function share(): Promise<void> {
  const url = window.location.href
  if (typeof navigator.share === 'function') {
    try {
      await navigator.share({ title: props.title, text: props.text, url })
      return
    } catch (error) {
      // Cancelar a folha de compartilhamento não é erro; outras falhas caem na cópia.
      if (error instanceof DOMException && error.name === 'AbortError') {
        return
      }
    }
  }
  await copy(url)
}
</script>
