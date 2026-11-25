<!--
  Painel opcional de curso ou área de estudo do onboarding: cursos do campus por
  nível e áreas do conhecimento, para quem estuda no IF ou não. Abre como
  `<dialog>` modal, lateral como os filtros do catálogo.
-->
<template>
  <dialog
    ref="dialog"
    class="study-dialog"
    aria-labelledby="study-dialog-title"
    @click="closeOnBackdrop"
  >
    <div class="flex h-full flex-col">
      <div class="flex items-center justify-between gap-3 border-b border-border px-4 py-3">
        <h2
          id="study-dialog-title"
          class="m-0 text-h3"
        >
          {{ t('onboarding.study.title') }}
        </h2>
        <button
          type="button"
          class="grid size-11 cursor-pointer place-items-center rounded-[50%] border-0 bg-transparent p-0 text-text hover:bg-surface-muted"
          :aria-label="t('onboarding.study.close')"
          @click="close"
        >
          <IconClose class="size-5" />
        </button>
      </div>

      <div class="grid min-h-0 flex-1 content-start gap-6 overflow-y-auto px-4 py-6">
        <p class="m-0 text-small text-text-muted">
          {{ t('onboarding.study.helper') }}
        </p>

        <fieldset
          v-for="group in coursesByLevel"
          :key="group.level"
          class="m-0 min-w-0 border-0 p-0"
        >
          <legend class="eyebrow float-left mb-3 w-full p-0">
            {{ t(`onboarding.study.levels.${group.level}`) }}
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
        <fieldset class="m-0 min-w-0 border-0 border-t border-border p-0 pt-6">
          <legend class="eyebrow float-left mb-3 w-full p-0">
            {{ t('onboarding.study.areasTitle') }}
          </legend>
          <div class="clear-both flex flex-wrap gap-2">
            <SelectableChip
              v-for="area in areas"
              :key="area.id"
              size="small"
              :selected="selectedAreaIds.includes(area.id)"
              @toggle="emit('toggleArea', area.id)"
            >
              {{ area.name }}
            </SelectableChip>
          </div>
        </fieldset>
      </div>

      <div class="border-t border-border px-4 py-3 pb-[max(var(--space-3),env(safe-area-inset-bottom))]">
        <button
          type="button"
          class="button button--primary w-full"
          @click="close"
        >
          {{ t('onboarding.study.done') }}
        </button>
      </div>
    </div>
  </dialog>
</template>

<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import IconClose from '../../../components/icons/IconClose.vue'
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

const dialog = useTemplateRef<HTMLDialogElement>('dialog')

function open(): void {
  dialog.value?.showModal()
}

function close(): void {
  dialog.value?.close()
}

// Um toque fora do painel (no fundo escurecido) fecha.
function closeOnBackdrop(event: MouseEvent): void {
  if (event.target === dialog.value) {
    close()
  }
}

defineExpose({ open })
</script>

<style scoped>
.study-dialog {
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

.study-dialog::backdrop {
  background: rgb(0 0 0 / 0.45);
}

@media (prefers-reduced-motion: no-preference) {
  .study-dialog[open] {
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
