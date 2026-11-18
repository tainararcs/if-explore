<!-- Filtros aplicados como pílulas removíveis, com a ação de limpar todos. -->
<template>
  <div
    v-if="items.length > 0"
    class="flex flex-wrap items-center gap-2"
  >
    <h2 class="sr-only">
      {{ t('catalog.filters.active') }}
    </h2>
    <ul class="m-0 flex list-none flex-wrap gap-2 p-0">
      <li
        v-for="item in items"
        :key="item.key"
      >
        <button
          type="button"
          class="inline-flex min-h-10 cursor-pointer items-center gap-1 rounded-pill border-[1.5px] border-primary bg-primary-soft py-0 pr-2 pl-3 font-body text-small font-semibold text-on-primary-soft"
          :aria-label="t('catalog.filters.remove', { name: item.label })"
          @click="emit('update', item.remove)"
        >
          {{ item.label }}
          <IconClose
            class="size-4"
            aria-hidden="true"
          />
        </button>
      </li>
    </ul>
    <button
      type="button"
      class="button button--ghost button--small"
      @click="emit('clear')"
    >
      {{ t('catalog.filters.clear') }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import IconClose from '../../../components/icons/IconClose.vue'
import type { Course, KnowledgeArea, LiteraryGenre } from '../../../models/taxonomy'
import { DEFAULT_TYPES, type CatalogState } from '../models/catalog-filters'

interface Props {
  state: CatalogState
  areas: KnowledgeArea[]
  courses: Course[]
  genres: LiteraryGenre[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  update: [changes: Partial<CatalogState>]
  clear: []
}>()

const { t } = useI18n()

interface ActiveFilter {
  key: string
  label: string
  /** Mudança que remove este filtro. */
  remove: Partial<CatalogState>
}

function nameOf(items: { id: string; name: string }[], id: string): string {
  return items.find((item) => item.id === id)?.name ?? id
}

const items = computed<ActiveFilter[]>(() => {
  const state = props.state
  const without = (list: readonly string[], id: string) => list.filter((item) => item !== id)
  const result: ActiveFilter[] = []
  const typesChanged =
    state.types.length !== DEFAULT_TYPES.length || DEFAULT_TYPES.some((type) => !state.types.includes(type))
  if (typesChanged) {
    for (const type of state.types) {
      result.push({
        key: `type-${type}`,
        label: t(`catalog.filters.types.${type}`),
        remove: { types: state.types.filter((item) => item !== type) },
      })
    }
  }
  if (state.availableOnly) {
    result.push({ key: 'available', label: t('catalog.filters.availableOnly'), remove: { availableOnly: false } })
  }
  for (const id of state.areaIds) {
    result.push({ key: `area-${id}`, label: nameOf(props.areas, id), remove: { areaIds: without(state.areaIds, id) } })
  }
  for (const id of state.courseIds) {
    result.push({
      key: `course-${id}`,
      label: nameOf(props.courses, id),
      remove: { courseIds: without(state.courseIds, id) },
    })
  }
  for (const id of state.genreIds) {
    result.push({
      key: `genre-${id}`,
      label: nameOf(props.genres, id),
      remove: { genreIds: without(state.genreIds, id) },
    })
  }
  for (const language of state.languages) {
    result.push({ key: `language-${language}`, label: language, remove: { languages: without(state.languages, language) } })
  }
  if (state.yearFrom !== null || state.yearTo !== null) {
    let label = t('catalog.filters.yearRange', { from: state.yearFrom, to: state.yearTo })
    if (state.yearTo === null) {
      label = t('catalog.filters.yearFromOnly', { year: state.yearFrom })
    } else if (state.yearFrom === null) {
      label = t('catalog.filters.yearToOnly', { year: state.yearTo })
    }
    result.push({ key: 'year', label, remove: { yearFrom: null, yearTo: null } })
  }
  return result
})
</script>
