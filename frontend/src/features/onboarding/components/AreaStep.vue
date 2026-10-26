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

    <section
      class="area-step__courses"
      aria-labelledby="area-step-courses-title"
    >
      <header class="area-step__courses-header">
        <h2
          id="area-step-courses-title"
          class="area-step__courses-title"
        >
          {{ t('onboarding.areas.coursesTitle') }}
        </h2>
        <p class="area-step__courses-helper">
          {{ t('onboarding.areas.coursesHelper') }}
        </p>
      </header>

      <fieldset
        v-for="group in coursesByLevel"
        :key="group.level"
        class="area-step__group area-step__course-group"
      >
        <legend class="area-step__course-legend eyebrow">
          {{ t(`onboarding.areas.levels.${group.level}`) }}
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
    </section>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import SelectableChip from '../../../components/SelectableChip.vue'
import type { Course, CourseLevel, KnowledgeArea } from '../../../models/taxonomy'

interface Props {
  areas: KnowledgeArea[]
  /** Todos os cursos do campus agrupados por nível de ensino. */
  coursesByLevel: { level: CourseLevel; courses: Course[] }[]
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
  gap: var(--space-4);
  margin-top: var(--space-6);
}

.area-step__courses-header {
  display: grid;
  gap: var(--space-1);
}

.area-step__courses-title {
  margin: 0;
  font-size: var(--text-body);
  font-weight: 600;
}

.area-step__courses-helper {
  margin: 0;
  font-size: var(--text-small);
  color: var(--color-text-muted);
}

.area-step__course-group {
  padding: var(--space-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
}

.area-step__course-legend {
  float: left;
  width: 100%;
  margin-bottom: var(--space-3);
  padding: 0;
}

.area-step__course-legend + .area-step__chips {
  clear: both;
}
</style>
