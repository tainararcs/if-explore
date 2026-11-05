<!-- Selo de disponibilidade com ponto + texto, para que o estado não dependa só da cor. -->
<template>
  <p
    class="m-0 inline-flex items-center gap-1 self-start rounded-pill bg-surface-muted px-2 py-0.5 text-caption font-semibold before:size-1.5 before:shrink-0 before:rounded-[50%] before:bg-current before:content-['']"
    :class="TONES[availability]"
  >
    {{ label }}
  </p>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { availabilityOf, type Availability, type Book } from '../models/book'

interface Props {
  book: Pick<Book, 'copies'>
  /**
   * Mostra a contagem de exemplares ("2 de 3 disponíveis") em vez do rótulo curto,
   * quando a consulta ao vivo trouxe a contagem exata.
   */
  detailed?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  detailed: false,
})

const TONES: Record<Availability, string> = {
  available: 'text-success',
  in_library_use: 'text-primary',
  on_loan: 'text-warning',
  unavailable: 'text-text-muted',
  uncertain: 'text-text-muted',
  no_copies: 'text-text-muted',
  unknown: 'text-text-muted',
}

const LABEL_KEYS: Record<Availability, string> = {
  available: 'common.availability.available',
  in_library_use: 'common.availability.libraryUse',
  on_loan: 'common.availability.borrowed',
  unavailable: 'common.availability.unavailable',
  uncertain: 'common.availability.uncertain',
  no_copies: 'common.availability.noCopies',
  unknown: 'common.availability.unknown',
}

const { t } = useI18n()

const availability = computed(() => availabilityOf(props.book))

const label = computed(() => {
  const { copies } = props.book
  if (props.detailed && copies?.status === 'available' && copies.available !== null) {
    const { available, total } = copies
    return t('common.availability.copies', { available, total }, total)
  }
  return t(LABEL_KEYS[availability.value])
})
</script>
