<!--
  Homepage: prateleiras de recomendações personalizadas, com a prateleira da IA em
  destaque no topo. A busca fica no catálogo completo (/catalog).
-->
<template>
  <div>
    <AppHeader sticky />

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

      <fieldset
        v-if="areas.length > 1"
        class="m-0 mt-6 min-w-0 border-0 p-0"
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

      <AiSuggestionShelf
        class="mt-8"
        :status="aiStatus"
        :items="visibleSuggestions"
        :message="aiMessage"
        :notice="aiNotice"
        :is-loading-more="aiLoadingMore"
        :area-names="areaNames"
        @request="requestSuggestions"
      />

      <div
        v-if="status === 'error'"
        class="mt-12"
        role="alert"
      >
        <p class="mb-4 text-danger">
          {{ t('home.error') }}
        </p>
        <button
          type="button"
          class="button button--secondary"
          @click="reload"
        >
          {{ t('home.retry') }}
        </button>
      </div>

      <div
        v-else-if="status === 'loading'"
        class="mt-12 grid gap-12"
        role="status"
      >
        <span class="sr-only">{{ t('home.loading') }}</span>
        <div
          v-for="shelf in 2"
          :key="shelf"
          aria-hidden="true"
        >
          <span class="skeleton mb-4 h-7 w-[min(280px,70%)] rounded-sm" />
          <div class="flex gap-4 overflow-hidden">
            <span
              v-for="item in 6"
              :key="item"
              class="skeleton aspect-[2/3] flex-[0_0_132px] rounded-cover md:basis-[160px]"
            />
          </div>
        </div>
      </div>

      <div
        v-else
        class="mt-12 grid grid-cols-[minmax(0,1fr)] gap-12 md:gap-16"
      >
        <BookShelf
          v-for="shelf in visibleShelves"
          :key="shelf.id"
          :title="shelfTitle(shelf)"
          :books="shelf.books"
          :featured="shelf.kind === 'forYou'"
        />
        <p
          v-if="visibleShelves.length === 0"
          class="text-text-muted"
        >
          {{ t('home.emptyFilter') }}
        </p>
        <div>
          <button
            type="button"
            class="button button--secondary"
            @click="showOtherSuggestions"
          >
            {{ t('home.shuffle') }}
          </button>
        </div>
      </div>
    </main>

    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import AppFooter from '../../../components/AppFooter.vue'
import AppHeader from '../../../components/AppHeader.vue'
import BookShelf from '../../../components/BookShelf.vue'
import SelectableChip from '../../../components/SelectableChip.vue'
import { getKnowledgeAreas } from '../../../services/catalog-service'
import AiSuggestionShelf from '../components/AiSuggestionShelf.vue'
import { useAiSuggestions } from '../composables/useAiSuggestions'
import { useHomeRecommendations } from '../composables/useHomeRecommendations'
import type { Shelf } from '../models/recommendation'

const { t } = useI18n()

const { status, shelves, areas, reload, shuffle } = useHomeRecommendations()
const activeAreaId = ref<string | null>(null)

// A IA não repete o que já está em destaque em "Escolhidos para você".
const forYouIds = computed(
  () => shelves.value.find((shelf) => shelf.kind === 'forYou')?.books.map((book) => book.id) ?? [],
)
const {
  status: aiStatus,
  items: aiItems,
  message: aiMessage,
  notice: aiNotice,
  isLoadingMore: aiLoadingMore,
  request: requestSuggestions,
} = useAiSuggestions(forYouIds)

// Nomes de todas as áreas, para os cards da IA (que podem sugerir fora das escolhidas).
const areaNames = ref(new Map<string, string>())
onMounted(async () => {
  try {
    areaNames.value = new Map((await getKnowledgeAreas()).map((area) => [area.id, area.name]))
  } catch {
    // Sem os nomes, os cards só não mostram a área.
  }
})

const areaList = computed(() =>
  new Intl.ListFormat('pt-BR', { type: 'conjunction' }).format(
    areas.value.map((area) => area.name),
  ),
)

const byActiveArea = (areaId: string | null) => activeAreaId.value === null || areaId === activeAreaId.value

// O filtro por área vale para todas as prateleiras; as que ficam vazias somem.
const visibleShelves = computed(() =>
  shelves.value
    .map((shelf) => ({ ...shelf, books: shelf.books.filter((book) => byActiveArea(book.areaId)) }))
    .filter((shelf) => shelf.books.length > 0),
)

const visibleSuggestions = computed(() => aiItems.value.filter((item) => byActiveArea(item.book.areaId)))

function shelfTitle(shelf: Shelf): string {
  return t(`home.shelves.${shelf.kind}`, { subject: shelf.subject ?? '' })
}

// A lista nova começa no topo; sem isso, o visitante ficaria no fim da página.
function showOtherSuggestions(): void {
  window.scrollTo({ top: 0 })
  void shuffle()
}
</script>
