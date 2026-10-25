<!-- Chip de seleção (liga/desliga) para áreas, cursos, gêneros e filtros. -->
<template>
  <button
    type="button"
    class="chip"
    :class="[`chip--${size}`, { 'chip--selected': selected }]"
    :aria-pressed="selected"
    @click="emit('toggle')"
  >
    <span
      class="chip__check"
      aria-hidden="true"
    >
      <IconCheck />
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

<style scoped>
.chip {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  min-height: 44px;
  padding: 0 var(--space-4);
  border: 1.5px solid transparent;
  border-radius: var(--radius-pill);
  background: var(--color-surface-muted);
  color: var(--color-text);
  font-family: var(--font-body);
  font-size: var(--text-body);
  font-weight: 500;
  line-height: 1.2;
  text-align: left;
  cursor: pointer;
  transition:
    background-color var(--duration-fast) var(--ease-standard),
    border-color var(--duration-fast) var(--ease-standard),
    color var(--duration-fast) var(--ease-standard);
}

.chip--small {
  min-height: 40px;
  padding: 0 var(--space-3);
  font-size: var(--text-small);
}

.chip:hover {
  border-color: var(--color-border);
}

.chip--selected,
.chip--selected:hover {
  border-color: var(--color-primary);
  background: var(--color-primary-soft);
  color: var(--color-primary);
  font-weight: 600;
}

/* O ícone de check reforça o estado selecionado além da cor. */
.chip__check {
  display: none;
  margin-inline-start: calc(var(--space-1) * -1);
}

.chip__check :deep(svg) {
  width: 18px;
  height: 18px;
}

.chip--selected .chip__check {
  display: inline-flex;
}
</style>
