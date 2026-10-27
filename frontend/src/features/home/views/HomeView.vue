<!-- Homepage: busca no acervo e prateleiras de recomendações personalizadas. -->
<template>
  <div>
    <AppHeader sticky>
      <template #actions>
        <RouterLink
          class="grid size-11 place-items-center rounded-[50%] text-primary hover:bg-surface-muted hover:text-primary"
          :to="{ path: '/onboarding', query: { step: 'areas' } }"
          :aria-label="t('home.adjustPreferences')"
          :title="t('home.adjustPreferences')"
        >
          <IconSparkle />
        </RouterLink>
      </template>
    </AppHeader>

    <main class="container pt-8 pb-16 md:pt-12">
      <div>
        <p class="eyebrow">
          {{ t('home.eyebrow') }}
        </p>
        <h1 class="mt-2">
          {{ t('home.title') }}
        </h1>
        <p
          v-if="areaList"
          class="mt-2 max-w-[60ch] text-text-muted"
        >
          {{ t('home.basis', { areas: areaList }) }}
        </p>
      </div>

      <SearchBar
        v-model="input"
        class="mt-6 max-w-[640px]"
        @clear="clear"
      />

      <fieldset
        v-if="areas.length > 1"
        class="m-0 mt-4 min-w-0 border-0 p-0"
      >
        <legend class="sr-only">
          {{ t('home.filterLegend') }}
        </legend>
        <!-- No celular os filtros rolam na horizontal em vez de quebrar linha. -->
        <div class="-mx-(--gutter) flex gap-2 overflow-x-auto px-(--gutter) py-1 [scrollbar-width:none] *:shrink-0 md:mx-0 md:flex-wrap md:overflow-visible md:px-0">
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
        class="mt-12"
        role="alert"
      >
        <p class="mb-4 text-danger">
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
        class="mt-12 grid gap-12"
        role="status"
      >
        <span class="sr-only">{{ t('home.loading') }}</span>
        <div
          v-for="shelf in 2"
          :key="shelf"
          aria-hidden="true"
        >
          <span class="home__pulse mb-4 block h-7 w-[min(280px,70%)] rounded-sm bg-surface-muted" />
          <div class="flex gap-4 overflow-hidden">
            <span
              v-for="item in 6"
              :key="item"
              class="home__pulse aspect-[2/3] flex-[0_0_132px] rounded-cover bg-surface-muted md:basis-[160px]"
            />
          </div>
        </div>
      </div>

      <SearchResults
        v-else-if="isSearching"
        class="mt-12"
        :query="query"
        :books="filteredResults"
        @clear="clear"
      />

      <div
        v-else
        class="mt-12 grid grid-cols-[minmax(0,1fr)] gap-12 md:gap-16"
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
          class="text-text-muted"
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
@media (prefers-reduced-motion: no-preference) {
  .home__pulse {
    animation: pulse 1.2s ease-in-out infinite alternate;
  }
}

@keyframes pulse {
  to {
    opacity: 0.5;
  }
}
</style>
