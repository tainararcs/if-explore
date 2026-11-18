<!--
  Catálogo completo: busca e filtros sobre todo o acervo, sem as regras das
  recomendações. Os filtros abrem num painel lateral pelo botão "Filtros", em
  qualquer tamanho de tela.
-->
<template>
  <div>
    <AppHeader sticky />

    <main class="container pt-8 pb-16 md:pt-12">
      <p class="eyebrow">
        {{ t('catalog.eyebrow') }}
      </p>
      <h1 class="mt-2">
        {{ t('catalog.title') }}
      </h1>
      <p class="mt-2 max-w-[60ch] text-text-muted">
        {{ t('catalog.lead') }}
      </p>

      <SearchBar
        v-model="input"
        class="mt-6 max-w-[640px]"
        @clear="input = ''"
      />

      <div class="mt-6 flex flex-wrap items-center gap-3">
        <button
          type="button"
          class="button button--secondary button--small"
          aria-haspopup="dialog"
          @click="openFilters"
        >
          <IconAdjustments
            class="size-5"
            aria-hidden="true"
          />
          {{ activeFilterCount > 0 ? t('catalog.filters.openWithCount', { n: activeFilterCount }) : t('catalog.filters.open') }}
        </button>
        <p
          v-if="status === 'ready'"
          class="m-0 text-small text-text-muted"
        >
          {{ countLabel }}
        </p>
        <label class="ms-auto flex items-center gap-2 text-small">
          {{ t('catalog.sort.label') }}
          <select
            class="sort-select"
            :value="currentSort"
            @change="onSortChange"
          >
            <option
              v-for="order in sortOptions"
              :key="order"
              :value="order"
            >
              {{ t(`catalog.sort.${order}`) }}
            </option>
          </select>
        </label>
      </div>

      <ActiveFilters
        class="mt-4"
        :state="state"
        :areas="areas"
        :courses="courses"
        :genres="genres"
        @update="update"
        @clear="clearFilters"
      />

      <div class="mt-8">
        <div>
          <div
            v-if="status === 'error'"
            role="alert"
          >
            <p class="mb-4 text-danger">
              {{ t('catalog.results.error') }}
            </p>
            <button
              type="button"
              class="button button--secondary"
              @click="reload"
            >
              {{ t('catalog.results.retry') }}
            </button>
          </div>

          <div
            v-else-if="status === 'loading'"
            class="grid grid-cols-2 gap-x-4 gap-y-8 sm:grid-cols-3 md:grid-cols-5 md:gap-x-6 lg:grid-cols-6"
            role="status"
          >
            <span class="sr-only">{{ t('catalog.results.loading') }}</span>
            <span
              v-for="item in 12"
              :key="item"
              class="skeleton aspect-[2/3] rounded-cover"
              aria-hidden="true"
            />
          </div>

          <CatalogResults
            v-else
            :query="state.query"
            :books="books"
            :total="total"
            :can-load-more="canLoadMore"
            :is-loading-more="isLoadingMore"
            :load-more-failed="loadMoreFailed"
            @clear-all="clearAll"
            @load-more="loadMore"
          />
        </div>
      </div>
    </main>

    <dialog
      ref="filtersDialog"
      class="filters-dialog"
      aria-labelledby="catalog-filters-title"
      @click="closeOnBackdrop"
    >
      <div class="flex h-full flex-col">
        <div class="flex items-center justify-between gap-3 border-b border-border px-4 py-3">
          <h2
            id="catalog-filters-title"
            class="m-0 text-h3"
          >
            {{ t('catalog.filters.title') }}
          </h2>
          <button
            type="button"
            class="grid size-11 cursor-pointer place-items-center rounded-[50%] border-0 bg-transparent p-0 text-text hover:bg-surface-muted"
            :aria-label="t('catalog.filters.close')"
            @click="closeFilters"
          >
            <IconClose class="size-5" />
          </button>
        </div>
        <div class="min-h-0 flex-1 overflow-y-auto px-4 py-6">
          <CatalogFilters
            :state="state"
            :areas="areas"
            :courses="courses"
            :genres="genres"
            :languages="languages"
            @update="update"
          />
        </div>
        <div class="flex gap-3 border-t border-border px-4 py-3 pb-[max(var(--space-3),env(safe-area-inset-bottom))]">
          <button
            v-if="activeFilterCount > 0"
            type="button"
            class="button button--ghost"
            @click="clearFilters"
          >
            {{ t('catalog.filters.clear') }}
          </button>
          <button
            type="button"
            class="button button--primary flex-1"
            @click="closeFilters"
          >
            {{ t('catalog.filters.showResults', { n: numbers.format(total) }, total) }}
          </button>
        </div>
      </div>
    </dialog>

    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import AppFooter from '../../../components/AppFooter.vue'
import AppHeader from '../../../components/AppHeader.vue'
import IconAdjustments from '../../../components/icons/IconAdjustments.vue'
import IconClose from '../../../components/icons/IconClose.vue'
import type { Course, KnowledgeArea, LiteraryGenre } from '../../../models/taxonomy'
import {
  getCourses,
  getKnowledgeAreas,
  getLanguages,
  getLiteraryGenres,
  SORT_ORDERS,
  type SortOrder,
} from '../../../services/catalog-service'
import ActiveFilters from '../components/ActiveFilters.vue'
import CatalogFilters from '../components/CatalogFilters.vue'
import CatalogResults from '../components/CatalogResults.vue'
import SearchBar from '../components/SearchBar.vue'
import { useCatalogBrowse } from '../composables/useCatalogBrowse'

const { t } = useI18n()
const numbers = new Intl.NumberFormat('pt-BR')

const {
  state,
  input,
  books,
  total,
  status,
  activeFilterCount,
  canLoadMore,
  isLoadingMore,
  loadMoreFailed,
  update,
  clearFilters,
  clearAll,
  loadMore,
  reload,
} = useCatalogBrowse()

const areas = ref<KnowledgeArea[]>([])
const courses = ref<Course[]>([])
const genres = ref<LiteraryGenre[]>([])
const languages = ref<string[]>([])

// Sem a taxonomia ou os idiomas, esses filtros só não aparecem.
onMounted(async () => {
  const [loadedAreas, loadedCourses, loadedGenres, loadedLanguages] = await Promise.allSettled([
    getKnowledgeAreas(),
    getCourses(),
    getLiteraryGenres(),
    getLanguages(),
  ])
  areas.value = loadedAreas.status === 'fulfilled' ? loadedAreas.value : []
  courses.value = loadedCourses.status === 'fulfilled' ? loadedCourses.value : []
  genres.value = loadedGenres.status === 'fulfilled' ? loadedGenres.value : []
  languages.value = loadedLanguages.status === 'fulfilled' ? loadedLanguages.value : []
})

const countLabel = computed(() =>
  state.value.query
    ? t('catalog.results.countFor', { query: state.value.query, n: numbers.format(total.value) }, total.value)
    : t('catalog.results.count', { n: numbers.format(total.value) }, total.value),
)

// "Relevância" só faz sentido com texto; sem ele, a ordem padrão é por exemplares.
const sortOptions = computed(() =>
  SORT_ORDERS.filter((order) => order !== 'relevance' || state.value.query !== ''),
)
const currentSort = computed<SortOrder>(() => {
  const sort = state.value.sort
  if (sort !== null && sortOptions.value.includes(sort)) {
    return sort
  }
  return state.value.query ? 'relevance' : 'popular'
})

function onSortChange(event: Event): void {
  if (!(event.target instanceof HTMLSelectElement)) {
    return
  }
  const value = event.target.value
  const sort = SORT_ORDERS.find((order) => order === value)
  if (sort) {
    update({ sort })
  }
}

const filtersDialog = useTemplateRef<HTMLDialogElement>('filtersDialog')

function openFilters(): void {
  filtersDialog.value?.showModal()
}

function closeFilters(): void {
  filtersDialog.value?.close()
}

// Um toque fora do painel (no fundo escurecido) fecha os filtros.
function closeOnBackdrop(event: MouseEvent): void {
  if (event.target === filtersDialog.value) {
    closeFilters()
  }
}
</script>

<style scoped>
.sort-select {
  min-height: 40px;
  border: 1.5px solid var(--color-border-strong);
  border-radius: var(--radius-pill);
  background: var(--color-surface);
  padding: 0 var(--space-3);
  color: var(--color-text);
  font: inherit;
}

.sort-select:hover {
  border-color: var(--color-primary-hover);
}

.filters-dialog {
  margin: 0;
  margin-inline-start: auto;
  width: min(100%, 420px);
  max-width: 100%;
  height: 100dvh;
  max-height: 100dvh;
  border: 0;
  background: var(--color-surface);
  padding: 0;
  color: var(--color-text);
}

.filters-dialog::backdrop {
  background: rgb(0 0 0 / 0.45);
}

@media (prefers-reduced-motion: no-preference) {
  .filters-dialog[open] {
    animation: slide-in var(--duration-base) var(--ease-standard);
  }
}

@keyframes slide-in {
  from {
    transform: translateX(16px);
    opacity: 0;
  }
}
</style>
