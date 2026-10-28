<!-- Selo de disponibilidade com ponto + texto, para que o estado não dependa só da cor. -->
<template>
  <p
    class="m-0 inline-flex items-center gap-1 self-start rounded-pill bg-surface-muted px-2 py-0.5 text-caption font-semibold before:size-1.5 before:shrink-0 before:rounded-[50%] before:bg-current before:content-['']"
    :class="isAvailable(book) ? 'text-success' : 'text-warning'"
  >
    {{ label }}
  </p>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { isAvailable, type Book } from '../models/book'

interface Props {
  book: Pick<Book, 'copies'>
  /** Mostra a contagem de exemplares ("2 de 3 disponíveis") em vez do rótulo curto. */
  detailed?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  detailed: false,
})

const { t } = useI18n()

const label = computed(() => {
  const { available, total } = props.book.copies
  if (props.detailed) {
    return available > 0
      ? t('common.availability.copies', { available, total }, total)
      : t('common.availability.allBorrowed', total)
  }
  return t(available > 0 ? 'common.availability.available' : 'common.availability.borrowed')
})
</script>
