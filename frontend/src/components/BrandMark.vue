<!-- Marca do IF Explore: grade de quadrados com um círculo, em referência à marca do Instituto Federal. -->
<template>
  <svg
    class="brand-mark"
    viewBox="0 0 34 46"
    aria-hidden="true"
    focusable="false"
  >
    <circle
      class="brand-mark__accent"
      cx="5"
      cy="5"
      r="5"
    />
    <rect
      v-for="cell in cells"
      :key="`${cell.x}-${cell.y}`"
      class="brand-mark__cell"
      :x="cell.x"
      :y="cell.y"
      width="10"
      height="10"
      rx="2"
    />
  </svg>
</template>

<script setup lang="ts">
// Posições das células conforme a marca: linhas com 2, 2, 3 e 2 quadrados.
const cells = [
  { x: 12, y: 0 },
  { x: 24, y: 0 },
  { x: 0, y: 12 },
  { x: 12, y: 12 },
  { x: 0, y: 24 },
  { x: 12, y: 24 },
  { x: 24, y: 24 },
  { x: 0, y: 36 },
  { x: 12, y: 36 },
]
</script>

<style scoped>
.brand-mark {
  display: block;
  height: 1.75rem;
  width: auto;
  flex-shrink: 0;
}

.brand-mark__accent {
  fill: var(--color-brand-accent);
}

.brand-mark__cell {
  fill: var(--color-primary);
}
</style>
