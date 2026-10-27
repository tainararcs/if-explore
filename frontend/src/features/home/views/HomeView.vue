<!-- Homepage: busca no acervo e prateleiras de recomendações personalizadas. -->
<template>
  <div class="home">
    <AppHeader sticky>
      <template #actions>
        <RouterLink
          class="home__adjust"
          :to="{ path: '/onboarding', query: { step: 'areas' } }"
          :aria-label="t('home.adjustPreferences')"
          :title="t('home.adjustPreferences')"
        >
          <IconSparkle />
        </RouterLink>
      </template>
    </AppHeader>

    <main class="home__main container">
      <div class="home__intro">
        <p class="eyebrow">
          {{ t('home.eyebrow') }}
        </p>
        <h1 class="home__title">
          {{ t('home.title') }}
        </h1>
        <p
          v-if="areaList"
          class="home__basis"
        >
          {{ t('home.basis', { areas: areaList }) }}
        </p>
      </div>

      <SearchBar
        v-model="input"
        class="home__search"
        @clear="clear"
      />

      <fieldset
        v-if="areas.length > 1"
        class="home__filter"
      >
        <legend class="sr-only">
          {{ t('home.filterLegend') }}
        </legend>
        <div class="home__filter-chips">
          <SelectableChip
            size="small"
            :selected="activeAreaId === null"
            @toggle="activeAreaId = null"
          >
            {{ t('home.allAreas') }}
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

      <div
        v-if="hasError"
        class="home__state"
        role="alert"
      >
        <p class="home__error">
          {{ t('home.error') }}
        </p>
        <button
          type="button"
          class="button button--secondary"
          @click="retry"
        >
          {{ t('home.retry') }}
        </button>
      </div>

      <div
        v-else-if="isLoading"
        class="home__skeleton"
        role="status"
      >
        <span class="sr-only">{{ t('home.loading') }}</span>
        <div
          v-for="shelf in 2"
          :key="shelf"
          class="home__skeleton-shelf"
          aria-hidden="true"
        >
          <span class="home__skeleton-title" />
          <div class="home__skeleton-row">
            <span
              v-for="item in 6"
              :key="item"
              class="home__skeleton-cover"
            />
          </div>
        </div>
      </div>

      <SearchResults
        v-else-if="isSearching"
        :query="query"
        :books="filteredResults"
        @clear="clear"
      />

      <div
        v-else
        class="home__shelves"
      >
        <BookShelf
          v-for="shelf in visibleShelves"
          :key="shelf.id"
          :title="shelfTitle(shelf)"
          :books="shelf.books"
          :show-quotes="shelf.kind === 'forYou'"
          :featured="shelf.kind === 'forYou'"
        />
        <p
          v-if="visibleShelves.length === 0"
          class="home__empty"
        >
          {{ t('home.emptyFilter') }}
        </p>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import AppHeader from '../../../components/AppHeader.vue'
import IconSparkle from '../../../components/icons/IconSparkle.vue'
import SelectableChip from '../../../components/SelectableChip.vue'
import BookShelf from '../components/BookShelf.vue'
import SearchBar from '../components/SearchBar.vue'
import SearchResults from '../components/SearchResults.vue'
import { useCatalogSearch } from '../composables/useCatalogSearch'
import { useHomeRecommendations } from '../composables/useHomeRecommendations'
import type { Shelf } from '../models/recommendation'

const { t } = useI18n()

const { status: shelvesStatus, shelves, areas, reload } = useHomeRecommendations()
const areaIds = computed(() => areas.value.map((area) => area.id))
const {
  input,
  query,
  isSearching,
  results,
  status: searchStatus,
  clear,
  reload: reloadSearch,
} = useCatalogSearch(areaIds)

const activeAreaId = ref<string | null>(null)

const isLoading = computed(
  () => shelvesStatus.value === 'loading' || searchStatus.value === 'loading',
)
const hasError = computed(() => shelvesStatus.value === 'error' || searchStatus.value === 'error')

const areaList = computed(() =>
  new Intl.ListFormat('pt-BR', { type: 'conjunction' }).format(
    areas.value.map((area) => area.name),
  ),
)

// O filtro por área vale para prateleiras e resultados; prateleiras vazias somem.
const visibleShelves = computed(() =>
  shelves.value
    .map((shelf) => ({
      ...shelf,
      books:
        activeAreaId.value === null
          ? shelf.books
          : shelf.books.filter((book) => book.areaId === activeAreaId.value),
    }))
    .filter((shelf) => shelf.books.length > 0),
)

const filteredResults = computed(() =>
  activeAreaId.value === null
    ? results.value
    : results.value.filter((book) => book.areaId === activeAreaId.value),
)

function shelfTitle(shelf: Shelf): string {
  return t(`home.shelves.${shelf.kind}`, { subject: shelf.subject ?? '' })
}

function retry(): void {
  if (shelvesStatus.value === 'error') {
    void reload()
  }
  if (searchStatus.value === 'error') {
    void reloadSearch()
  }
}
</script>

<style scoped>
.home__main {
  padding-block: var(--space-6) var(--space-8);
}

.home__adjust {
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  border-radius: 50%;
  color: var(--color-primary);
}

.home__adjust:hover {
  background: var(--color-surface-muted);
  color: var(--color-primary);
}

.home__title {
  margin-top: var(--space-2);
}

.home__basis {
  max-width: 60ch;
  margin-top: var(--space-2);
  color: var(--color-text-muted);
}

.home__search {
  max-width: 640px;
  margin-top: var(--space-5);
}

.home__filter {
  min-width: 0;
  margin: var(--space-4) 0 0;
  padding: 0;
  border: 0;
}

/* No celular os filtros rolam na horizontal em vez de quebrar linha. */
.home__filter-chips {
  display: flex;
  gap: var(--space-2);
  margin-inline: calc(var(--gutter) * -1);
  padding: var(--space-1) var(--gutter);
  overflow-x: auto;
  scrollbar-width: none;
}

.home__filter-chips > * {
  flex-shrink: 0;
}

.home__shelves,
.home__skeleton,
.home__state,
:deep(.search-results) {
  margin-top: var(--space-7);
}

/* minmax(0, 1fr) impede que a largura das prateleiras roláveis estique a página. */
.home__shelves {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: var(--space-7);
}

.home__error {
  margin-bottom: var(--space-4);
  color: var(--color-danger);
}

.home__empty {
  color: var(--color-text-muted);
}

.home__skeleton {
  display: grid;
  gap: var(--space-7);
}

.home__skeleton-title {
  display: block;
  width: min(280px, 70%);
  height: 1.75rem;
  margin-bottom: var(--space-4);
  border-radius: var(--radius-sm);
  background: var(--color-surface-muted);
}

.home__skeleton-row {
  display: flex;
  gap: var(--space-4);
  overflow: hidden;
}

.home__skeleton-cover {
  flex: 0 0 132px;
  aspect-ratio: 2 / 3;
  border-radius: var(--radius-cover);
  background: var(--color-surface-muted);
}

@media (min-width: 900px) {
  .home__main {
    padding-top: var(--space-7);
  }

  .home__filter-chips {
    flex-wrap: wrap;
    margin-inline: 0;
    padding-inline: 0;
    overflow: visible;
  }

  .home__shelves {
    gap: var(--space-8);
  }

  .home__skeleton-cover {
    flex-basis: 160px;
  }
}

@media (prefers-reduced-motion: no-preference) {
  .home__skeleton-title,
  .home__skeleton-cover {
    animation: pulse 1.2s ease-in-out infinite alternate;
  }
}

@keyframes pulse {
  to {
    opacity: 0.5;
  }
}
</style>
