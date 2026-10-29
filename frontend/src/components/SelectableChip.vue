<!-- Chip de seleção (liga/desliga) para áreas, cursos, gêneros e filtros. -->
<template>
  <button
    type="button"
    class="inline-flex cursor-pointer items-center gap-1 rounded-pill border-[1.5px] font-body leading-[1.2] text-left transition-[background-color,border-color,color] duration-(--duration-fast) ease-standard"
    :class="[
      size === 'small' ? 'min-h-10 px-3 py-0 text-small' : 'min-h-11 px-4 py-0 text-body',
      selected
        ? 'border-primary bg-primary-soft font-semibold text-on-primary-soft'
        : 'border-chip-border bg-surface-muted font-medium text-text hover:border-border-strong',
    ]"
    :aria-pressed="selected"
    @click="emit('toggle')"
  >
    <!-- O ícone de check reforça o estado selecionado além da cor. -->
    <span
      class="-ms-1"
      :class="selected ? 'inline-flex' : 'hidden'"
      aria-hidden="true"
    >
      <IconCheck class="size-[18px]" />
    </span>
    <slot />
  </button>
</template>

<script setup lang="ts">
import IconCheck from './icons/IconCheck.vue'

interface Props {
  selected: boolean
  size?: 'medium' | 'small'
}

withDefaults(defineProps<Props>(), {
  size: 'medium',
})

const emit = defineEmits<{
  toggle: []
}>()
</script>
