<!-- Passo 1 do onboarding: grandes áreas (obrigatório) e, opcionalmente, cursos do campus. -->
<template>
  <div class="area-step">
    <fieldset class="area-step__group">
      <legend class="visually-hidden">
        {{ t('onboarding.areas.legend') }}
      </legend>
      <div class="area-step__chips">
        <SelectableChip
          v-for="area in areas"
          :key="area.id"
          :selected="selectedAreaIds.includes(area.id)"
          @toggle="emit('toggleArea', area.id)"
        >
          {{ area.name }}
        </SelectableChip>
      </div>
    </fieldset>

    <TransitionGroup
      tag="div"
      name="course-group"
      class="area-step__courses"
    >
      <fieldset
        v-for="group in coursesBySelectedArea"
        :key="group.area.id"
        class="area-step__group area-step__course-group"
      >
        <legend class="area-step__course-legend">
          <span class="eyebrow">{{ group.area.name }}</span>
          <span class="area-step__course-question">{{ t('onboarding.areas.coursesQuestion') }}</span>
        </legend>
        <div class="area-step__chips">
          <SelectableChip
            v-for="course in group.courses"
            :key="course.id"
            size="small"
            :selected="selectedCourseIds.includes(course.id)"
            @toggle="emit('toggleCourse', course.id)"
          >
            {{ course.name }}
          </SelectableChip>
        </div>
      </fieldset>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import SelectableChip from '../../../components/SelectableChip.vue'
import type { Course, KnowledgeArea } from '../../../models/taxonomy'

interface Props {
  areas: KnowledgeArea[]
  /** Cursos do campus agrupados apenas pelas áreas já escolhidas. */
  coursesBySelectedArea: { area: KnowledgeArea; courses: Course[] }[]
  selectedAreaIds: string[]
  selectedCourseIds: string[]
}

defineProps<Props>()

const emit = defineEmits<{
  toggleArea: [areaId: string]
  toggleCourse: [courseId: string]
}>()

const { t } = useI18n()
</script>

<style scoped>
.area-step__group {
  margin: 0;
  padding: 0;
  border: 0;
  min-width: 0;
}

.area-step__chips {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.area-step__courses {
  display: grid;
  gap: var(--space-5);
  margin-top: var(--space-6);
}

.area-step__course-group {
  padding: var(--space-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
}

.area-step__course-legend {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  float: left;
  width: 100%;
  margin-bottom: var(--space-3);
  padding: 0;
}

.area-step__course-legend + .area-step__chips {
  clear: both;
}

.area-step__course-question {
  font-size: var(--text-small);
  color: var(--color-text-muted);
}

@media (prefers-reduced-motion: no-preference) {
  .course-group-enter-active,
  .course-group-leave-active {
    transition:
      opacity var(--duration-base) var(--ease-standard),
      transform var(--duration-base) var(--ease-standard);
  }

  .course-group-enter-from,
  .course-group-leave-to {
    opacity: 0;
    transform: translateY(calc(var(--space-2) * -1));
  }

  .course-group-leave-active {
    position: absolute;
    visibility: hidden;
  }
}
</style>
