<!--
  Onboarding "Descobrir minhas leituras" em uma tela: a pessoa toca em três títulos
  de um mural de capas, filtrável por gênero; curso e área do campus são opcionais.
  Os gêneros das preferências são deduzidos dos títulos escolhidos.
-->
<template>
  <div class="flex min-h-dvh flex-col">
    <AppHeader focus />

    <main class="flex-1 overflow-x-clip pb-12">
      <div class="container pt-2 sm:pt-4">
        <RouterLink
          to="/"
          class="button button--ghost button--small -ms-3 px-3"
        >
          <IconArrowLeft class="size-5" />
          {{ t('onboarding.back') }}
        </RouterLink>
      </div>

      <div
        v-if="status === 'loading'"
        class="container pt-4"
        role="status"
      >
        <span class="sr-only">{{ t('onboarding.loading') }}</span>
        <div
          class="grid gap-4"
          aria-hidden="true"
        >
          <span class="skeleton h-10 max-w-[480px] rounded-sm" />
          <span class="skeleton h-10 rounded-pill" />
          <span class="skeleton h-14 rounded-md" />
        </div>
      </div>

      <div
        v-else-if="status === 'error'"
        class="container pt-4"
        role="alert"
      >
        <p class="mb-4 text-danger">
          {{ t('onboarding.error') }}
        </p>
        <button
          type="button"
          class="button button--secondary"
          @click="load"
        >
          {{ t('onboarding.retry') }}
        </button>
      </div>

      <section
        v-else
        class="container pt-4"
        aria-labelledby="onboarding-title"
      >
        <h1 id="onboarding-title">
          {{ t('onboarding.title') }}
        </h1>
        <p class="mt-2 text-text-muted">
          {{ t('onboarding.helper') }}
        </p>

        <div class="mt-5 grid gap-3">
          <CandidateFilters
            :genres="genres"
            :areas="selectedAreas"
            :active="activeFilter"
            @select="selectFilter"
          />

          <button
            type="button"
            class="flex w-full cursor-pointer items-center gap-3 rounded-md border-0 bg-surface px-4 py-2.5 text-left text-text hover:bg-surface-muted sm:max-w-[480px]"
            aria-haspopup="dialog"
            @click="studyDialog?.open()"
          >
            <span class="grid min-w-0 flex-1 gap-0.5">
              <span class="font-semibold">{{ t('onboarding.study.title') }}</span>
              <span class="truncate text-small text-text-muted">{{ studySummary }}</span>
            </span>
            <IconArrowRight class="size-5 shrink-0 text-text-muted" />
          </button>
        </div>

        <BookWall
          class="mt-6"
          :books="visibleBooks"
          :selected-ids="draft.seedBookIds"
          :limit-reached="isComplete"
          :status="candidatesStatus"
          @toggle-book="toggleBook"
          @retry="loadCandidates"
        />
      </section>
    </main>

    <OnboardingActionBar v-if="status === 'ready'">
      <template #hint>
        <span
          class="inline-flex items-center gap-3 font-semibold"
          :class="attempted && !isComplete ? 'text-danger' : 'text-text'"
        >
          <span
            class="inline-flex gap-1"
            aria-hidden="true"
          >
            <span
              v-for="slot in REQUIRED_SEED_BOOKS"
              :key="slot"
              class="size-2.5 rounded-[50%] border-[1.5px] border-primary transition-[background-color] duration-(--duration-fast) ease-standard"
              :class="{ 'bg-primary': slot <= draft.seedBookIds.length }"
            />
          </span>
          {{ isComplete ? t('onboarding.books.complete') : t('onboarding.books.missing', missingBooks) }}
        </span>
      </template>

      <button
        type="button"
        class="button button--primary"
        @click="complete"
      >
        {{ t('onboarding.recommend') }}
        <span class="button__arrow"><IconArrowRight /></span>
      </button>
    </OnboardingActionBar>

    <StudyDialog
      ref="studyDialog"
      :areas="areas"
      :courses-by-level="coursesByLevel"
      :selected-area-ids="draft.areaIds"
      :selected-course-ids="draft.courseIds"
      @toggle-area="toggleArea"
      @toggle-course="toggleCourse"
    />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import AppHeader from '../../../components/AppHeader.vue'
import IconArrowLeft from '../../../components/icons/IconArrowLeft.vue'
import IconArrowRight from '../../../components/icons/IconArrowRight.vue'
import { REQUIRED_SEED_BOOKS } from '../../../models/reading-preferences'
import BookWall from '../components/BookWall.vue'
import CandidateFilters from '../components/CandidateFilters.vue'
import OnboardingActionBar from '../components/OnboardingActionBar.vue'
import StudyDialog from '../components/StudyDialog.vue'
import { useTasteOnboarding } from '../composables/useTasteOnboarding'

const { t } = useI18n()
const router = useRouter()

const {
  status,
  genres,
  areas,
  coursesByLevel,
  selectedAreas,
  selectedCourses,
  draft,
  activeFilter,
  visibleBooks,
  candidatesStatus,
  isComplete,
  missingBooks,
  load,
  loadCandidates,
  selectFilter,
  toggleArea,
  toggleCourse,
  toggleBook,
  finish,
} = useTasteOnboarding()

const studyDialog = useTemplateRef<InstanceType<typeof StudyDialog>>('studyDialog')
// Marca que a pessoa tentou concluir sem os três títulos, para destacar o que falta.
const attempted = ref(false)

/** O que foi escolhido no painel de curso ou área: cursos, ou áreas sem curso. */
const studySummary = computed(() => {
  const names =
    selectedCourses.value.length > 0
      ? selectedCourses.value.map((course) => course.name)
      : selectedAreas.value.map((area) => area.name)
  return names.length > 0
    ? new Intl.ListFormat('pt-BR', { type: 'conjunction' }).format(names)
    : t('onboarding.study.summaryEmpty')
})

function complete(): void {
  if (finish()) {
    void router.push('/home')
    return
  }
  attempted.value = true
}

onMounted(load)
</script>
