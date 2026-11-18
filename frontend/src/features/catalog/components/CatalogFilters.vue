<!--
  Filtros do catálogo: tipo, disponibilidade, área, curso (por nível), gênero,
  idioma e ano de publicação. Mostra quantos livros cada opção traria; opções sem
  livros somem, a não ser que estejam marcadas.
-->
<template>
  <div class="flex flex-col gap-8">
    <fieldset class="filter-group">
      <legend class="filter-legend">
        {{ t('catalog.filters.type') }}
      </legend>
      <div class="flex flex-wrap gap-2">
        <SelectableChip
          v-for="type in BOOK_TYPES"
          :key="type"
          size="small"
          :selected="state.types.includes(type)"
          @toggle="emit('update', { types: toggled(state.types, type) })"
        >
          {{ label(t(`catalog.filters.types.${type}`), countOf(facets?.types, type)) }}
        </SelectableChip>
      </div>
    </fieldset>

    <fieldset class="filter-group">
      <legend class="filter-legend">
        {{ t('catalog.filters.availability') }}
      </legend>
      <div class="flex flex-wrap gap-2">
        <SelectableChip
          size="small"
          :selected="state.availableOnly"
          @toggle="emit('update', { availableOnly: !state.availableOnly })"
        >
          {{ label(t('catalog.filters.availableOnly'), facets?.available) }}
        </SelectableChip>
      </div>
    </fieldset>

    <fieldset
      v-if="visibleAreas.length > 0"
      class="filter-group"
    >
      <legend class="filter-legend">
        {{ t('catalog.filters.area') }}
      </legend>
      <div class="flex flex-wrap gap-2">
        <SelectableChip
          v-for="area in visibleAreas"
          :key="area.id"
          size="small"
          :selected="state.areaIds.includes(area.id)"
          @toggle="emit('update', { areaIds: toggled(state.areaIds, area.id) })"
        >
          {{ label(area.name, countOf(facets?.areas, area.id)) }}
        </SelectableChip>
      </div>
    </fieldset>

    <fieldset
      v-if="courseGroups.length > 0"
      class="filter-group"
    >
      <legend class="filter-legend">
        {{ t('catalog.filters.course') }}
      </legend>
      <div
        v-for="group in courseGroups"
        :key="group.level"
        class="mt-3 first-of-type:mt-0"
      >
        <p class="m-0 mb-2 text-caption text-text-muted">
          {{ t(`onboarding.areas.levels.${group.level}`) }}
        </p>
        <div class="flex flex-wrap gap-2">
          <SelectableChip
            v-for="course in group.courses"
            :key="course.id"
            size="small"
            :selected="state.courseIds.includes(course.id)"
            @toggle="emit('update', { courseIds: toggled(state.courseIds, course.id) })"
          >
            {{ label(course.name, countOf(facets?.courses, course.id)) }}
          </SelectableChip>
        </div>
      </div>
    </fieldset>

    <fieldset
      v-if="visibleGenres.length > 0"
      class="filter-group"
    >
      <legend class="filter-legend">
        {{ t('catalog.filters.genre') }}
      </legend>
      <div class="flex flex-wrap gap-2">
        <SelectableChip
          v-for="genre in visibleGenres"
          :key="genre.id"
          size="small"
          :selected="state.genreIds.includes(genre.id)"
          @toggle="emit('update', { genreIds: toggled(state.genreIds, genre.id) })"
        >
          {{ label(genre.name, countOf(facets?.genres, genre.id)) }}
        </SelectableChip>
      </div>
    </fieldset>

    <fieldset
      v-if="languages.length > 0"
      class="filter-group"
    >
      <legend class="filter-legend">
        {{ t('catalog.filters.language') }}
      </legend>
      <div class="flex flex-wrap gap-2">
        <SelectableChip
          v-for="language in languages"
          :key="language.id"
          size="small"
          :selected="state.languages.includes(language.id)"
          @toggle="emit('update', { languages: toggled(state.languages, language.id) })"
        >
          {{ label(language.id, language.count) }}
        </SelectableChip>
      </div>
    </fieldset>

    <fieldset class="filter-group">
      <legend class="filter-legend">
        {{ t('catalog.filters.year') }}
      </legend>
      <form
        class="flex items-end gap-3"
        @submit.prevent="applyYears"
      >
        <label class="flex min-w-0 flex-1 flex-col gap-1 text-small">
          {{ t('catalog.filters.yearFrom') }}
          <input
            v-model="yearFrom"
            class="year-input"
            type="number"
            inputmode="numeric"
            :min="MIN_YEAR"
            :max="maxYear"
            :placeholder="String(MIN_YEAR)"
            @change="applyYears"
          >
        </label>
        <label class="flex min-w-0 flex-1 flex-col gap-1 text-small">
          {{ t('catalog.filters.yearTo') }}
          <input
            v-model="yearTo"
            class="year-input"
            type="number"
            inputmode="numeric"
            :min="MIN_YEAR"
            :max="maxYear"
            :placeholder="String(maxYear)"
            @change="applyYears"
          >
        </label>
      </form>
    </fieldset>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import SelectableChip from '../../../components/SelectableChip.vue'
import { COURSE_LEVELS, type Course, type KnowledgeArea, type LiteraryGenre } from '../../../models/taxonomy'
import { BOOK_TYPES } from '../../../services/catalog-service'
import type { CatalogFacets, CatalogState, FacetCount } from '../models/catalog-filters'

interface Props {
  state: CatalogState
  /** Contagens dos filtros; `null` enquanto carregam (as opções aparecem sem números). */
  facets: CatalogFacets | null
  areas: KnowledgeArea[]
  courses: Course[]
  genres: LiteraryGenre[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  update: [changes: Partial<CatalogState>]
}>()

const { t } = useI18n()
const numbers = new Intl.NumberFormat('pt-BR')

// O acervo tem títulos do século XVIII; o campo aceita qualquer ano até o atual.
const MIN_YEAR = 1700
const maxYear = new Date().getFullYear()

function toggled<T extends string>(items: readonly T[], item: T): T[] {
  return items.includes(item) ? items.filter((value) => value !== item) : [...items, item]
}

/** Com as contagens carregadas, opção ausente nelas traria 0 livros. */
function countOf(counts: Map<string, number> | undefined, id: string): number | undefined {
  return counts === undefined ? undefined : (counts.get(id) ?? 0)
}

function label(name: string, count: number | undefined): string {
  return count === undefined ? name : t('catalog.filters.option', { name, count: numbers.format(count) })
}

/** Com contagens, some a opção que não traria livros, a não ser que esteja marcada. */
function isVisible(id: string, counts: Map<string, number> | undefined, selected: readonly string[]): boolean {
  return counts === undefined || (counts.get(id) ?? 0) > 0 || selected.includes(id)
}

const visibleAreas = computed(() =>
  props.areas.filter((area) => isVisible(area.id, props.facets?.areas, props.state.areaIds)),
)

const visibleGenres = computed(() =>
  props.genres.filter((genre) => isVisible(genre.id, props.facets?.genres, props.state.genreIds)),
)

const courseGroups = computed(() =>
  COURSE_LEVELS.map((level) => ({
    level,
    courses: props.courses.filter(
      (course) =>
        course.level === level && isVisible(course.id, props.facets?.courses, props.state.courseIds),
    ),
  })).filter((group) => group.courses.length > 0),
)

/** Idiomas do acervo e, se um marcado não tiver livros agora, ele também. */
const languages = computed<FacetCount[]>(() => {
  const known = props.facets?.languages ?? []
  const missing = props.state.languages
    .filter((language) => !known.some((item) => item.id === language))
    .map((language) => ({ id: language, count: 0 }))
  return [...known, ...missing]
})

// O v-model de um campo numérico entrega número quando o texto é um número válido.
const yearFrom = ref<string | number>(props.state.yearFrom ?? '')
const yearTo = ref<string | number>(props.state.yearTo ?? '')

watch(
  () => [props.state.yearFrom, props.state.yearTo] as const,
  ([from, to]) => {
    yearFrom.value = from ?? ''
    yearTo.value = to ?? ''
  },
)

function parseYear(value: string | number): number | null {
  const year = Number(value)
  return String(value).trim() === '' || !Number.isInteger(year) ? null : Math.min(Math.max(year, 0), 9999)
}

/** Aplica a faixa de anos; se vier invertida, troca as pontas. */
function applyYears(): void {
  let from = parseYear(yearFrom.value)
  let to = parseYear(yearTo.value)
  if (from !== null && to !== null && from > to) {
    ;[from, to] = [to, from]
  }
  if (from !== props.state.yearFrom || to !== props.state.yearTo) {
    emit('update', { yearFrom: from, yearTo: to })
  }
}
</script>

<style scoped>
.filter-group {
  margin: 0;
  min-width: 0;
  border: 0;
  padding: 0;
}

.filter-legend {
  margin-bottom: var(--space-3);
  padding: 0;
  font-family: var(--font-body);
  font-size: var(--text-small);
  font-weight: 600;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--color-text-muted);
}

.year-input {
  min-height: 44px;
  width: 100%;
  border: 1.5px solid var(--color-border-strong);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  padding: 0 var(--space-3);
  color: var(--color-text);
  font: inherit;
}

.year-input:hover {
  border-color: var(--color-primary-hover);
}
</style>
