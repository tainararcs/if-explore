<!--
  Destaque da página do livro: faixa tingida com a cor da capa, capa (fixa ao
  rolar no desktop), título e disponibilidade. O slot recebe o restante do
  conteúdo, que fica na coluna de detalhes a partir de 900px.
-->
<template>
  <div
    class="book-hero"
    :style="{ '--band-tone': tone }"
  >
    <div class="container grid gap-6 pt-2 md:grid-cols-[240px_minmax(0,1fr)] md:gap-12 md:pt-6">
      <div class="book-hero__cover mx-auto w-36 md:mx-0 md:w-full">
        <BookCover :book="book" />
      </div>

      <div class="min-w-0">
        <div class="flex flex-col items-center gap-2 text-center md:items-start md:text-left">
          <p class="eyebrow">
            {{ eyebrow }}
          </p>
          <h1
            ref="heading"
            class="book-hero__title outline-none"
            tabindex="-1"
          >
            {{ book.title }}
          </h1>
          <p class="text-body text-text-muted">
            {{ book.authors.join(', ') }}
          </p>
          <AvailabilityBadge
            class="mt-1 self-center md:self-start"
            :book="book"
            detailed
          />
        </div>
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'
import AvailabilityBadge from '../../../components/AvailabilityBadge.vue'
import BookCover from '../../../components/BookCover.vue'
import { pickCoverColor } from '../../../lib/cover-color'
import type { Book } from '../../../models/book'

interface Props {
  book: Book
  /** Linha acima do título, como "Área · ano". */
  eyebrow: string
}

const props = defineProps<Props>()

const heading = useTemplateRef<HTMLHeadingElement>('heading')
const tone = computed(() => pickCoverColor(props.book.id))

defineExpose({
  /** Move o foco para o título, ao trocar de livro pela prateleira de relacionados. */
  focusHeading: () => heading.value?.focus(),
})
</script>

<style scoped>
/*
  Faixa de fundo na cor da capa, misturada ao papel para manter o contraste do
  texto; no escuro a mistura é mais forte para a cor continuar perceptível.
  Ela se dissolve no fundo da página na parte de baixo.
*/
.book-hero {
  --band-height: 360px;

  position: relative;
  isolation: isolate;
}

.book-hero::before {
  content: '';
  position: absolute;
  inset: 0 0 auto;
  z-index: -1;
  height: var(--band-height);
  background: linear-gradient(
    to bottom,
    light-dark(
        color-mix(in srgb, var(--band-tone) 20%, var(--color-bg)),
        color-mix(in srgb, var(--band-tone) 45%, var(--color-bg))
      )
      55%,
    var(--color-bg)
  );
}

.book-hero__title {
  font-size: var(--text-h1);
}

@media (min-width: 900px) {
  .book-hero {
    --band-height: 300px;
  }

  .book-hero__cover {
    position: sticky;
    top: calc(var(--header-height) + var(--space-6));
    align-self: start;
  }

  .book-hero__title {
    font-size: var(--text-display);
    line-height: 1.05;
  }
}
</style>
