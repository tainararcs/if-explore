<!-- Passo 2 do onboarding: escolha de exatamente três títulos entre os candidatos das áreas escolhidas. -->
<template>
  <div>
    <fieldset
      v-if="areas.length > 1"
      class="m-0 mb-6 min-w-0 border-0 p-0"
    >
      <legend class="sr-only">
        {{ t('onboarding.books.filterLegend') }}
      </legend>
      <div class="flex flex-wrap gap-2">
        <SelectableChip
          size="small"
          :selected="activeAreaId === null"
          @toggle="activeAreaId = null"
        >
          {{ t('onboarding.books.allAreas') }}
        </SelectableChip>
        <SelectableChip
          v-for="area in areas"
          :key="area.id"
          size="small"
          :selected="activeAreaId === area.id"
          @toggle="activeAreaId = area.id"
        >
          {{ area.name }}
        </SelectableChip>
      </div>
    </fieldset>

    <ul class="m-0 grid list-none grid-cols-3 gap-x-3 gap-y-6 p-0 sm:grid-cols-4 sm:gap-x-4 sm:gap-y-8 md:grid-cols-6">
      <li
        v-for="book in visibleBooks"
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
          >{{ book.authors.join(', ') }}</span>
        </button>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import BookCover from '../../../components/BookCover.vue'
import IconCheck from '../../../components/icons/IconCheck.vue'
import SelectableChip from '../../../components/SelectableChip.vue'
import type { Book } from '../../../models/book'
import type { KnowledgeArea } from '../../../models/taxonomy'

interface Props {
  /** Candidatos já ordenados por relevância. */
  books: Book[]
  /** Áreas escolhidas, usadas como filtro quando há mais de uma. */
  areas: KnowledgeArea[]
  selectedIds: string[]
  /** Indica que o limite de títulos foi atingido. */
  limitReached: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  toggleBook: [bookId: string]
}>()

const { t } = useI18n()

const activeAreaId = ref<string | null>(null)

const visibleBooks = computed(() =>
  activeAreaId.value === null
    ? props.books
    : props.books.filter((book) => book.areaId === activeAreaId.value),
)

function isSelected(bookId: string): boolean {
  return props.selectedIds.includes(bookId)
}

function isLocked(bookId: string): boolean {
  return props.limitReached && !isSelected(bookId)
}
</script>
