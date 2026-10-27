<!-- Passo opcional do onboarding: gêneros literários para leitura fora da sala de aula. -->
<template>
  <fieldset class="m-0 min-w-0 border-0 p-0">
    <legend class="sr-only">
      {{ t('onboarding.genres.legend') }}
    </legend>
    <div class="flex flex-wrap gap-2">
      <SelectableChip
        v-for="genre in genres"
        :key="genre.id"
        :selected="selectedIds.includes(genre.id)"
        @toggle="emit('toggleGenre', genre.id)"
      >
        {{ genre.name }}
      </SelectableChip>
    </div>
  </fieldset>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import SelectableChip from '../../../components/SelectableChip.vue'
import type { LiteraryGenre } from '../../../models/taxonomy'

interface Props {
  genres: LiteraryGenre[]
  selectedIds: string[]
}

defineProps<Props>()

const emit = defineEmits<{
  toggleGenre: [genreId: string]
}>()

const { t } = useI18n()
</script>
