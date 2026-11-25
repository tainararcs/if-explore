<!--
  Recortes do mural do onboarding: "Todos", cada gênero literário e as áreas
  escolhidas. No celular os chips rolam na horizontal em vez de quebrar linha.
-->
<template>
  <fieldset class="m-0 min-w-0 border-0 p-0">
    <legend class="sr-only">
      {{ t('onboarding.filters.legend') }}
    </legend>
    <div class="-mx-(--gutter) flex gap-2 overflow-x-auto px-(--gutter) py-1 [scrollbar-width:none] *:shrink-0 md:mx-0 md:flex-wrap md:overflow-visible md:px-0">
      <SelectableChip
        size="small"
        :selected="active.kind === 'all'"
        @toggle="emit('select', ALL_CANDIDATES)"
      >
        {{ t('onboarding.filters.all') }}
      </SelectableChip>
      <SelectableChip
        v-for="genre in genres"
        :key="genre.id"
        size="small"
        :selected="active.kind === 'genre' && active.id === genre.id"
        @toggle="emit('select', { kind: 'genre', id: genre.id })"
      >
        {{ genre.name }}
      </SelectableChip>
      <SelectableChip
        v-for="area in areas"
        :key="area.id"
        size="small"
        :selected="active.kind === 'area' && active.id === area.id"
        @toggle="emit('select', { kind: 'area', id: area.id })"
      >
        {{ area.name }}
      </SelectableChip>
    </div>
  </fieldset>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import SelectableChip from '../../../components/SelectableChip.vue'
import type { KnowledgeArea, LiteraryGenre } from '../../../models/taxonomy'
import { ALL_CANDIDATES, type CandidateFilter } from '../models/onboarding-draft'

interface Props {
  genres: LiteraryGenre[]
  /** Áreas escolhidas pela pessoa, listadas depois dos gêneros. */
  areas: KnowledgeArea[]
  active: CandidateFilter
}

defineProps<Props>()

const emit = defineEmits<{
  select: [filter: CandidateFilter]
}>()

const { t } = useI18n()
</script>
