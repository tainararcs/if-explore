<!-- Seção "Em poucas palavras": explicação simplificada do livro gerada por IA, com o aviso de origem. -->
<template>
  <section
    v-if="isLoading || text"
    aria-labelledby="book-explanation-title"
  >
    <h2
      id="book-explanation-title"
      class="mb-3 flex items-center gap-2 font-body text-h3 font-semibold"
    >
      <IconSparkle class="size-5 text-primary" />
      {{ t('bookDetail.explanation.title') }}
    </h2>
    <div
      v-if="isLoading"
      class="grid max-w-[65ch] gap-2"
      role="status"
    >
      <span class="sr-only">{{ t('bookDetail.explanation.loading') }}</span>
      <span
        class="book-explanation__pulse block h-4 w-full rounded-sm bg-surface-muted"
        aria-hidden="true"
      />
      <span
        class="book-explanation__pulse block h-4 w-3/4 rounded-sm bg-surface-muted"
        aria-hidden="true"
      />
    </div>
    <template v-else>
      <p class="m-0 max-w-[65ch] text-body">
        {{ text }}
      </p>
      <p class="m-0 mt-2 text-caption text-text-muted">
        {{ t('bookDetail.explanation.note') }}
      </p>
    </template>
  </section>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import IconSparkle from '../../../components/icons/IconSparkle.vue'

interface Props {
  text: string | null
  isLoading: boolean
}

defineProps<Props>()

const { t } = useI18n()
</script>

<style scoped>
@media (prefers-reduced-motion: no-preference) {
  .book-explanation__pulse {
    animation: pulse 1.2s ease-in-out infinite alternate;
  }
}

@keyframes pulse {
  to {
    opacity: 0.5;
  }
}
</style>
