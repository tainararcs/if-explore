<!-- Marca do IF Explore: grade de quadrados com um círculo, em referência à marca do Instituto Federal. -->
<template>
  <svg
    class="block h-7 w-auto shrink-0"
    viewBox="0 0 34 46"
    aria-hidden="true"
    focusable="false"
  >
    <circle
      class="fill-brand-accent"
      cx="5"
      cy="5"
      r="5"
    />
    <rect
      v-for="cell in cells"
      :key="`${cell.x}-${cell.y}`"
      class="fill-primary"
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
