<!-- Passo 2 do onboarding: escolha de exatamente três títulos entre os candidatos das áreas escolhidas. -->
<template>
  <div class="book-pick">
    <fieldset
      v-if="areas.length > 1"
      class="book-pick__filter"
    >
      <legend class="sr-only">
        {{ t('onboarding.books.filterLegend') }}
      </legend>
      <div class="book-pick__filter-chips">
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

    <ul class="book-pick__grid">
      <li
        v-for="book in visibleBooks"
        :key="book.id"
      >
        <button
          type="button"
          class="book-pick__card"
          :class="{
            'book-pick__card--selected': isSelected(book.id),
            'book-pick__card--locked': isLocked(book.id),
          }"
          :aria-pressed="isSelected(book.id)"
          :aria-disabled="isLocked(book.id) || undefined"
          @click="emit('toggleBook', book.id)"
        >
          <span class="book-pick__cover">
            <BookCover
              :book="book"
              decorative
            />
            <span
              v-if="isSelected(book.id)"
              class="book-pick__badge"
              aria-hidden="true"
            >
              <IconCheck />
            </span>
          </span>
          <span class="book-pick__title">{{ book.title }}</span>
          <span class="book-pick__author">{{ book.authors.join(', ') }}</span>
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

<style scoped>
.book-pick__filter {
  margin: 0 0 var(--space-5);
  padding: 0;
  border: 0;
  min-width: 0;
}

.book-pick__filter-chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.book-pick__grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-5) var(--space-3);
  margin: 0;
  padding: 0;
  list-style: none;
}

.book-pick__card {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  width: 100%;
  padding: 0;
  border: 0;
  background: none;
  color: var(--color-text);
  text-align: left;
  cursor: pointer;
}

.book-pick__card[aria-disabled='true'] {
  cursor: not-allowed;
}

.book-pick__cover {
  position: relative;
  display: block;
  margin-bottom: var(--space-2);
  border-radius: var(--radius-cover);
  outline: 3px solid transparent;
  outline-offset: 3px;
  transition:
    outline-color var(--duration-fast) var(--ease-standard),
    opacity var(--duration-fast) var(--ease-standard),
    transform var(--duration-fast) var(--ease-standard);
}

.book-pick__card--selected .book-pick__cover {
  outline-color: var(--color-primary);
}

.book-pick__card--locked .book-pick__cover,
.book-pick__card--locked .book-pick__title,
.book-pick__card--locked .book-pick__author {
  opacity: 0.45;
}

.book-pick__badge {
  position: absolute;
  top: calc(var(--space-2) * -1);
  right: calc(var(--space-2) * -1);
  display: grid;
  place-items: center;
  width: 32px;
  height: 32px;
  border: 2px solid var(--color-bg);
  border-radius: 50%;
  background: var(--color-primary);
  color: var(--color-on-primary);
}

.book-pick__badge :deep(svg) {
  width: 18px;
  height: 18px;
  stroke-width: 2.5;
}

.book-pick__title {
  font-size: var(--text-small);
  font-weight: 600;
  line-height: 1.3;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.book-pick__author {
  font-size: var(--text-caption);
  color: var(--color-text-muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

@media (min-width: 600px) {
  .book-pick__grid {
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: var(--space-6) var(--space-4);
  }

  .book-pick__title {
    font-size: var(--text-body);
  }

  .book-pick__author {
    font-size: var(--text-small);
  }
}

@media (min-width: 900px) {
  .book-pick__grid {
    grid-template-columns: repeat(6, minmax(0, 1fr));
  }
}

@media (prefers-reduced-motion: no-preference) {
  .book-pick__card:not([aria-disabled='true']):hover .book-pick__cover {
    transform: translateY(-2px);
  }
}
</style>
