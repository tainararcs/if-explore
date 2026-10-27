<!-- Passo 1 do onboarding: grandes áreas (obrigatório) e, opcionalmente, cursos do campus. -->
<template>
  <div>
    <fieldset class="m-0 min-w-0 border-0 p-0">
      <legend class="sr-only">
        {{ t('onboarding.areas.legend') }}
      </legend>
      <div class="flex flex-wrap gap-2">
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
      class="mt-8 grid gap-4"
      aria-labelledby="area-step-courses-title"
    >
      <header class="grid gap-1">
        <h2
          id="area-step-courses-title"
          class="m-0 text-body font-semibold"
        >
          {{ t('onboarding.areas.coursesTitle') }}
        </h2>
        <p class="m-0 text-small text-text-muted">
          {{ t('onboarding.areas.coursesHelper') }}
        </p>
      </header>

      <fieldset
        v-for="group in coursesByLevel"
        :key="group.level"
        class="m-0 min-w-0 rounded-md border border-border bg-surface p-4"
      >
        <legend class="eyebrow float-left mb-3 w-full p-0">
          {{ t(`onboarding.areas.levels.${group.level}`) }}
        </legend>
        <div class="clear-both flex flex-wrap gap-2">
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
