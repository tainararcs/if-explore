<!--
  Botão "Ler prévia" e o diálogo com o leitor do Google Livros. O leitor só é
  carregado quando o visitante abre o diálogo e é descartado ao fechar.
-->
<template>
  <button
    v-bind="$attrs"
    type="button"
    class="button button--secondary"
    @click="open"
  >
    <IconBookOpen class="size-5" />
    {{ t('bookDetail.preview.action') }}
  </button>

  <dialog
    ref="dialog"
    class="book-preview m-auto flex-col gap-3 rounded-lg border border-border bg-surface p-3 text-text shadow-md md:p-4"
    aria-labelledby="book-preview-title"
    @close="isOpen = false"
    @click="closeOnBackdrop"
  >
    <div class="flex items-center justify-between gap-3">
      <div class="min-w-0">
        <h2
          id="book-preview-title"
          class="m-0 truncate font-body text-h3 font-semibold"
        >
          {{ t('bookDetail.preview.title', { title: bookTitle }) }}
        </h2>
        <p class="m-0 text-caption text-text-muted">
          {{ t('bookDetail.preview.source') }}
        </p>
      </div>
      <button
        type="button"
        class="button button--ghost button--small shrink-0 px-3"
        :aria-label="t('bookDetail.preview.close')"
        @click="close"
      >
        <IconClose class="size-5" />
      </button>
    </div>
    <iframe
      v-if="isOpen"
      class="min-h-0 w-full flex-1 rounded-md border-0 bg-bg"
      :src="embedUrl"
      :title="t('bookDetail.preview.frameTitle', { title: bookTitle })"
      sandbox="allow-scripts allow-same-origin allow-popups allow-popups-to-escape-sandbox"
      referrerpolicy="strict-origin-when-cross-origin"
      allowfullscreen
    />
  </dialog>
</template>

<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import IconBookOpen from '../../../components/icons/IconBookOpen.vue'
import IconClose from '../../../components/icons/IconClose.vue'

interface Props {
  /** Endereço do leitor embutível do Google Livros. */
  embedUrl: string
  bookTitle: string
}

defineOptions({ inheritAttrs: false })

defineProps<Props>()

const { t } = useI18n()

const dialog = useTemplateRef<HTMLDialogElement>('dialog')
const isOpen = ref(false)

function open(): void {
  isOpen.value = true
  dialog.value?.showModal()
}

function close(): void {
  dialog.value?.close()
}

// Um clique fora do conteúdo atinge o próprio <dialog> (o fundo), e não um filho.
function closeOnBackdrop(event: MouseEvent): void {
  if (event.target === dialog.value) {
    close()
  }
}
</script>

<style scoped>
.book-preview {
  width: min(960px, 100% - 2 * var(--space-4));
  height: min(900px, 100dvh - 2 * var(--space-4));
  max-width: none;
  max-height: none;
}

.book-preview[open] {
  display: flex;
}

.book-preview::backdrop {
  background: rgb(0 0 0 / 0.55);
}
</style>
