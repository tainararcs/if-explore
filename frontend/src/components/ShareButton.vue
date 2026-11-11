<!--
  Compartilha o link do livro: usa o compartilhamento nativo quando o navegador
  oferece (celulares) e, nos demais casos, copia o link.
-->
<template>
  <button
    type="button"
    class="button button--secondary"
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
import IconCheck from '../../../components/icons/IconCheck.vue'
import IconShare from '../../../components/icons/IconShare.vue'
import { useClipboardFeedback } from '../../../composables/useClipboardFeedback'

interface Props {
  /** Título do livro, usado no texto do compartilhamento. */
  title: string
}

const props = defineProps<Props>()

const { t } = useI18n()
const { state: copyState, copy } = useClipboardFeedback()

const label = computed(() => {
  if (copyState.value === 'copied') {
    return t('bookDetail.share.copied')
  }
  return copyState.value === 'failed' ? t('bookDetail.share.failed') : t('bookDetail.share.action')
})

async function share(): Promise<void> {
  const url = window.location.href
  if (typeof navigator.share === 'function') {
    try {
      await navigator.share({ title: props.title, text: t('bookDetail.share.text', { title: props.title }), url })
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
