<!--
  Painel opcional "Estuda no IF?" do onboarding: busca de curso do campus e áreas
  do conhecimento. Abre como `<dialog>` modal, lateral como os filtros do catálogo.
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

        <div class="relative flex items-center">
          <label
            for="study-dialog-search"
            class="sr-only"
          >
            {{ t('onboarding.study.searchLabel') }}
          </label>
          <IconSearch class="pointer-events-none absolute left-4 size-5 text-text-muted" />
          <input
            id="study-dialog-search"
            v-model="query"
            class="min-h-12 w-full appearance-none rounded-pill border-[1.5px] border-border-strong bg-surface py-0 pr-4 pl-12 text-text [font:inherit] placeholder:text-text-muted hover:border-primary-hover focus-visible:border-primary focus-visible:outline-3 focus-visible:outline-offset-0 focus-visible:outline-primary/30 [&::-webkit-search-cancel-button]:hidden"
            type="search"
            autocomplete="off"
            :placeholder="t('onboarding.study.searchPlaceholder')"
          >
        </div>

        <fieldset
          v-for="group in visibleGroups"
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
        <p
          v-if="visibleGroups.length === 0"
          class="m-0 text-small text-text-muted"
          role="status"
        >
          {{ t('onboarding.study.noCourses') }}
        </p>

        <fieldset class="m-0 min-w-0 border-0 border-t border-border p-0 pt-6">
          <legend class="float-left mb-1 w-full p-0 text-body font-semibold">
            {{ t('onboarding.study.areasTitle') }}
          </legend>
          <p class="clear-both mb-3 text-small text-text-muted">
            {{ t('onboarding.study.areasHelper') }}
          </p>
          <div class="flex flex-wrap gap-2">
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
import { computed, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import IconClose from '../../../components/icons/IconClose.vue'
import IconSearch from '../../../components/icons/IconSearch.vue'
import SelectableChip from '../../../components/SelectableChip.vue'
import type { Course, CourseLevel, KnowledgeArea } from '../../../models/taxonomy'

interface Props {
  areas: KnowledgeArea[]
  /** Todos os cursos do campus agrupados por nível de ensino. */
  coursesByLevel: { level: CourseLevel; courses: Course[] }[]
  selectedAreaIds: string[]
  selectedCourseIds: string[]
}

const props = defineProps<Props>()

const emit = defineEmits<{
  toggleArea: [areaId: string]
  toggleCourse: [courseId: string]
}>()

const { t } = useI18n()

const dialog = useTemplateRef<HTMLDialogElement>('dialog')
const query = ref('')

// Compara sem acentos e sem diferenciar maiúsculas ("informatica" acha "Informática").
function normalize(text: string): string {
  return text.normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase()
}

/** Cursos que contêm o texto buscado, sem níveis vazios. */
const visibleGroups = computed(() => {
  const term = normalize(query.value.trim())
  if (!term) {
    return props.coursesByLevel
  }
  return props.coursesByLevel
    .map((group) => ({
      ...group,
      courses: group.courses.filter((course) => normalize(course.name).includes(term)),
    }))
    .filter((group) => group.courses.length > 0)
})

function open(): void {
  query.value = ''
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
