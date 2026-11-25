<!-- Mural de capas do onboarding: a pessoa toca em exatamente três títulos que leria. -->
<template>
  <div>
    <div
      v-if="status === 'error' && books.length === 0"
      class="py-8"
      role="alert"
    >
      <p class="mb-4 text-danger">
        {{ t('onboarding.books.error') }}
      </p>
      <button
        type="button"
        class="button button--secondary"
        @click="emit('retry')"
      >
        {{ t('onboarding.books.retry') }}
      </button>
    </div>

    <ul
      v-else-if="status === 'loading' && books.length === 0"
      class="m-0 grid list-none grid-cols-3 gap-x-3 gap-y-6 p-0 sm:grid-cols-4 sm:gap-x-4 md:grid-cols-6"
      role="status"
      :aria-label="t('onboarding.books.loading')"
    >
      <li
        v-for="index in 12"
        :key="index"
        class="skeleton aspect-[2/3] rounded-cover"
        aria-hidden="true"
      />
    </ul>

    <template v-else>
      <ul
        class="m-0 grid list-none grid-cols-3 gap-x-3 gap-y-6 p-0 motion-safe:transition-opacity motion-safe:duration-(--duration-base) sm:grid-cols-4 sm:gap-x-4 sm:gap-y-8 md:grid-cols-6"
        :class="{ 'opacity-60': status === 'loading' }"
        :aria-busy="status === 'loading'"
      >
        <li
          v-for="book in books"
          :key="book.id"
        >
          <button
            type="button"
            class="group flex w-full cursor-pointer flex-col gap-1 border-0 bg-transparent p-0 text-left text-text aria-disabled:cursor-not-allowed"
            :aria-pressed="isSelected(book.id)"
            :aria-disabled="isLocked(book.id) || undefined"
            @click="emit('toggleBook', book.id)"
          >
            <span
              class="relative mb-2 block rounded-cover outline-3 outline-offset-3 transition-[outline-color,opacity,translate] duration-(--duration-fast) ease-standard"
              :class="[
                isSelected(book.id) ? 'outline-primary' : 'outline-transparent',
                isLocked(book.id) ? 'opacity-45' : 'motion-safe:group-hover:-translate-y-0.5',
              ]"
            >
              <BookCover
                :book="book"
                decorative
              />
              <span
                v-if="isSelected(book.id)"
                class="absolute -top-2 -right-2 grid size-8 place-items-center rounded-[50%] border-2 border-bg bg-primary text-on-primary"
                aria-hidden="true"
              >
                <IconCheck class="size-[18px] stroke-[2.5]" />
              </span>
            </span>
            <span
              class="line-clamp-2 text-small leading-[1.3] font-semibold sm:text-body"
              :class="{ 'opacity-45': isLocked(book.id) }"
            >{{ book.title }}</span>
            <span
              class="truncate text-caption text-text-muted sm:text-small"
              :class="{ 'opacity-45': isLocked(book.id) }"
            >{{ formatAuthors(book.authors) }}</span>
          </button>
        </li>
      </ul>

      <div
        v-if="hasMore"
        class="mt-8 flex justify-center"
      >
        <button
          type="button"
          class="button button--secondary"
          @click="emit('showMore')"
        >
          {{ t('onboarding.books.showMore') }}
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import BookCover from '../../../components/BookCover.vue'
import IconCheck from '../../../components/icons/IconCheck.vue'
import { formatAuthors } from '../../../lib/catalog-format'
import type { Book } from '../../../models/book'

interface Props {
  /** Títulos visíveis do recorte atual, com os já escolhidos primeiro. */
  books: Book[]
  selectedIds: string[]
  /** Indica que o limite de títulos foi atingido. */
  limitReached: boolean
  /** Carregamento do recorte; sem títulos ainda, mostra capas de espera. */
  status: 'loading' | 'ready' | 'error'
  /** Há mais títulos do recorte além dos visíveis. */
  hasMore: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  toggleBook: [bookId: string]
  retry: []
  showMore: []
}>()

const { t } = useI18n()

function isSelected(bookId: string): boolean {
  return props.selectedIds.includes(bookId)
}

function isLocked(bookId: string): boolean {
  return props.limitReached && !isSelected(bookId)
}
</script>
