<!-- Onboarding "Descobrir minhas leituras": áreas, três títulos e refinamento opcional por gêneros. -->
<template>
  <div class="flex min-h-dvh flex-col">
    <AppHeader />

    <main class="flex-1 overflow-x-clip pb-12">
      <div class="container flex items-center gap-3 py-3 sm:py-4">
        <button
          type="button"
          class="button button--ghost button--small -ms-3 shrink-0 px-3"
          @click="goBack"
        >
          <IconArrowLeft class="size-5" />
          {{ t('onboarding.back') }}
        </button>
        <OnboardingProgress :step="currentStep" />
      </div>

      <div
        v-if="status === 'loading'"
        class="container max-w-[720px] pt-6 sm:pt-8"
        role="status"
      >
        <span class="sr-only">{{ t('onboarding.loading') }}</span>
        <div
          class="onboarding__skeleton flex flex-wrap gap-2"
          aria-hidden="true"
        >
          <span class="mb-6 h-10 basis-full rounded-sm bg-surface-muted" />
          <span
            v-for="index in 8"
            :key="index"
            class="h-11 w-32 rounded-pill bg-surface-muted nth-[3n]:w-[180px]"
          />
        </div>
      </div>

      <div
        v-else-if="status === 'error'"
        class="container max-w-[720px] pt-6 sm:pt-8"
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

      <Transition
        v-else
        :name="`step-${direction}`"
        mode="out-in"
        @after-enter="focusHeading"
      >
        <section
          :key="currentStep"
          class="container pt-6 sm:pt-8"
          :class="{ 'max-w-[720px]': currentStep !== 'books' }"
          aria-labelledby="onboarding-title"
        >
          <h1
            id="onboarding-title"
            ref="heading"
            class="outline-none"
            tabindex="-1"
          >
            {{ t(`onboarding.${currentStep}.title`) }}
          </h1>
          <p class="mt-2 mb-8 text-text-muted">
            {{ t(`onboarding.${currentStep}.helper`) }}
          </p>

          <AreaStep
            v-if="currentStep === 'areas'"
            :areas="areas"
            :courses-by-level="coursesByLevel"
            :selected-area-ids="draft.areaIds"
            :selected-course-ids="draft.courseIds"
            @toggle-area="toggleArea"
            @toggle-course="toggleCourse"
          />
          <BookPickStep
            v-else-if="currentStep === 'books'"
            :books="candidateBooks"
            :areas="selectedAreas"
            :selected-ids="draft.seedBookIds"
            :limit-reached="isBooksComplete"
            @toggle-book="toggleBook"
          />
          <GenreStep
            v-else
            :genres="genres"
            :selected-ids="draft.genreIds"
            @toggle-genre="toggleGenre"
          />
        </section>
      </Transition>
    </main>

    <OnboardingActionBar v-if="status === 'ready'">
      <template #hint>
        <template v-if="currentStep === 'areas'">
          {{
            canLeaveAreas
              ? t('onboarding.areas.selected', draft.areaIds.length)
              : t('onboarding.areas.hint')
          }}
        </template>
        <span
          v-else-if="currentStep === 'books'"
          class="inline-flex items-center gap-3 font-semibold text-text"
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
          {{
            isBooksComplete
              ? t('onboarding.books.complete')
              : t('onboarding.books.missing', missingBooks)
          }}
        </span>
        <template v-else>
          {{ t('onboarding.genres.selected', draft.genreIds.length) }}
        </template>
      </template>

      <button
        v-if="currentStep === 'areas'"
        type="button"
        class="button button--primary"
        :disabled="!canLeaveAreas"
        @click="goTo('books')"
      >
        {{ t('onboarding.areas.continue') }}
        <span class="button__arrow"><IconArrowRight /></span>
      </button>
      <template v-else-if="currentStep === 'books'">
        <button
          type="button"
          class="button button--secondary"
          :disabled="!isBooksComplete"
          @click="goTo('genres')"
        >
          {{ t('onboarding.books.refine') }}
        </button>
        <button
          type="button"
          class="button button--primary"
          :disabled="!isBooksComplete"
          @click="complete"
        >
          {{ t('onboarding.recommend') }}
          <span class="button__arrow"><IconArrowRight /></span>
        </button>
      </template>
      <button
        v-else
        type="button"
        class="button button--primary"
        @click="complete"
      >
        {{ t('onboarding.recommend') }}
        <span class="button__arrow"><IconArrowRight /></span>
      </button>
    </OnboardingActionBar>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, useRouter } from 'vue-router'
import AppHeader from '../../../components/AppHeader.vue'
import IconArrowLeft from '../../../components/icons/IconArrowLeft.vue'
import IconArrowRight from '../../../components/icons/IconArrowRight.vue'
import { REQUIRED_SEED_BOOKS } from '../../../models/reading-preferences'
import AreaStep from '../components/AreaStep.vue'
import BookPickStep from '../components/BookPickStep.vue'
import GenreStep from '../components/GenreStep.vue'
import OnboardingActionBar from '../components/OnboardingActionBar.vue'
import OnboardingProgress from '../components/OnboardingProgress.vue'
import { useTasteOnboarding } from '../composables/useTasteOnboarding'
import {
  ONBOARDING_STEPS,
  isOnboardingStep,
  stepIndex,
  type OnboardingStep,
} from '../models/onboarding-draft'

const { t } = useI18n()
const route = useRoute()
const router = useRouter()

const {
  status,
  areas,
  genres,
  draft,
  candidateBooks,
  coursesByLevel,
  canLeaveAreas,
  isBooksComplete,
  furthestStep,
  missingBooks,
  load,
  toggleArea,
  toggleCourse,
  toggleBook,
  toggleGenre,
  finish,
} = useTasteOnboarding()

const heading = useTemplateRef<HTMLHeadingElement>('heading')
const direction = ref<'forward' | 'back'>('forward')

const selectedAreas = computed(() =>
  areas.value.filter((area) => draft.value.areaIds.includes(area.id)),
)

// O passo vem da URL, limitado ao mais avançado que as escolhas permitem.
const currentStep = computed<OnboardingStep>(() => {
  const requested = route.query.step
  if (!isOnboardingStep(requested)) {
    return 'areas'
  }
  return stepIndex(requested) <= stepIndex(furthestStep.value) ? requested : furthestStep.value
})

// Corrige a URL quando ela aponta para um passo inválido ou ainda inacessível.
watch(
  [() => route.query.step, currentStep, status],
  ([requested, step, loadStatus]) => {
    if (loadStatus === 'ready' && requested !== step) {
      void router.replace({ query: { step } })
    }
  },
)

watch(currentStep, (next, previous) => {
  direction.value = stepIndex(next) >= stepIndex(previous) ? 'forward' : 'back'
})

function focusHeading(): void {
  heading.value?.focus()
}

function goTo(step: OnboardingStep): void {
  void router.push({ query: { step } })
}

function goBack(): void {
  if (currentStep.value === 'areas') {
    void router.push('/')
    return
  }
  // Volta pelo histórico quando a página anterior é o passo anterior do fluxo.
  const back = router.options.history.state.back
  if (typeof back === 'string' && back.startsWith('/onboarding')) {
    router.back()
    return
  }
  const previous = ONBOARDING_STEPS[stepIndex(currentStep.value) - 1] ?? 'areas'
  void router.replace({ query: { step: previous } })
}

function complete(): void {
  if (finish()) {
    void router.push('/home')
  }
}

onMounted(load)
</script>

<style scoped>
@media (prefers-reduced-motion: no-preference) {
  .onboarding__skeleton > * {
    animation: pulse 1.2s ease-in-out infinite alternate;
  }

  /* Troca de passo: desliza na direção da navegação. */
  .step-forward-enter-active,
  .step-forward-leave-active,
  .step-back-enter-active,
  .step-back-leave-active {
    transition:
      opacity var(--duration-base) var(--ease-standard),
      transform var(--duration-base) var(--ease-standard);
  }

  .step-forward-enter-from,
  .step-back-leave-to {
    opacity: 0;
    transform: translateX(12px);
  }

  .step-forward-leave-to,
  .step-back-enter-from {
    opacity: 0;
    transform: translateX(-12px);
  }
}

@keyframes pulse {
  to {
    opacity: 0.5;
  }
}
</style>
