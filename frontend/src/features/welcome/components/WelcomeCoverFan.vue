<!-- Leque decorativo de capas usado como ilustração da tela de boas-vindas. -->
<template>
  <ul
    class="cover-fan"
    aria-hidden="true"
  >
    <li
      v-for="item in items"
      :key="item.book.id"
      class="cover-fan__item"
      :style="{ '--offset': item.offset, '--depth': item.depth }"
    >
      <BookCover
        :book="item.book"
        decorative
      />
    </li>
  </ul>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import BookCover from '../../../components/BookCover.vue'
import type { Book } from '../../../models/book'

interface Props {
  books: Book[]
}

const props = defineProps<Props>()

// Distribui as capas simetricamente a partir do centro do leque.
const items = computed(() => {
  const center = (props.books.length - 1) / 2
  return props.books.map((book, index) => ({
    book,
    offset: index - center,
    depth: Math.abs(index - center),
  }))
})
</script>

<style scoped>
.cover-fan {
  --cover-width: clamp(96px, 27vw, 132px);
  --spread: 1;
  --step: 38%;

  position: relative;
  height: calc(var(--cover-width) * 1.5 + var(--space-6));
  margin: 0;
  padding: 0;
  list-style: none;
}

.cover-fan__item {
  position: absolute;
  top: calc(var(--depth) * var(--space-2));
  left: 50%;
  width: var(--cover-width);
  z-index: calc(10 - var(--depth));
  transform: translateX(calc(-50% + var(--offset) * var(--spread) * var(--step)))
    rotate(calc(var(--offset) * var(--spread) * 6deg));
  transform-origin: 50% 100%;
}

@media (min-width: 900px) {
  .cover-fan {
    --cover-width: 168px;
    --step: 30%;
  }
}

@media (prefers-reduced-motion: no-preference) {
  .cover-fan__item {
    animation: fan-in var(--duration-base) var(--ease-standard) both;
    animation-delay: calc(var(--depth) * 60ms);
    transition: transform var(--duration-base) var(--ease-standard);
  }

  .cover-fan:hover {
    --spread: 1.2;
  }
}

@keyframes fan-in {
  from {
    opacity: 0;
    translate: 0 var(--space-4);
  }
}
</style>
