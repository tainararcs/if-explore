<!-- Passo opcional do onboarding: gêneros literários para leitura fora da sala de aula. -->
<template>
  <fieldset class="genre-step">
    <legend class="visually-hidden">
      {{ t('onboarding.genres.legend') }}
    </legend>
    <div class="genre-step__chips">
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

<style scoped>
.genre-step {
  margin: 0;
  padding: 0;
  border: 0;
  min-width: 0;
}

.genre-step__chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}
</style>
