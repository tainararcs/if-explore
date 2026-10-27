<!-- Onboarding "Descobrir minhas leituras": áreas, três títulos e refinamento opcional por gêneros. -->
<template>
  <div class="onboarding">
    <AppHeader />

    <main class="onboarding__main">
      <div class="onboarding__topbar container">
        <button
          type="button"
          class="button button--ghost button--small onboarding__back"
          @click="goBack"
        >
          <IconArrowLeft />
          {{ t('onboarding.back') }}
        </button>
        <OnboardingProgress :step="currentStep" />
      </div>

      <div
        v-if="status === 'loading'"
        class="onboarding__step onboarding__step--narrow container"
        role="status"
      >
        <span class="sr-only">{{ t('onboarding.loading') }}</span>
        <div
          class="onboarding__skeleton"
          aria-hidden="true"
        >
          <span class="onboarding__skeleton-title" />
          <span
            v-for="index in 8"
            :key="index"
            class="onboarding__skeleton-chip"
          />
        </div>
      </div>

      <div
        v-else-if="status === 'error'"
        class="onboarding__step onboarding__step--narrow container"
        role="alert"
      >
        <p class="onboarding__error">
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
          class="onboarding__step container"
          :class="{ 'onboarding__step--narrow': currentStep !== 'books' }"
          aria-labelledby="onboarding-title"
        >
          <h1
            id="onboarding-title"
            ref="heading"
            class="onboarding__title"
            tabindex="-1"
          >
            {{ t(`onboarding.${currentStep}.title`) }}
          </h1>
          <p class="onboarding__helper">
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
          class="onboarding__counter"
        >
          <span
            class="onboarding__slots"
            aria-hidden="true"
          >
            <span
              v-for="slot in REQUIRED_SEED_BOOKS"
              :key="slot"
              class="onboarding__slot"
              :class="{ 'onboarding__slot--filled': slot <= draft.seedBookIds.length }"
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
.onboarding {
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
}

.onboarding__main {
  flex: 1;
  padding-bottom: var(--space-7);
  overflow-x: clip;
}

.onboarding__topbar {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding-block: var(--space-3);
}

.onboarding__back {
  flex-shrink: 0;
  margin-inline-start: calc(var(--space-3) * -1);
  padding-inline: var(--space-3);
}

.onboarding__back :deep(svg) {
  width: 20px;
  height: 20px;
}

.onboarding__step {
  padding-top: var(--space-5);
}

.onboarding__step--narrow {
  max-width: 720px;
}

.onboarding__title {
  outline: none;
}

.onboarding__helper {
  margin: var(--space-2) 0 var(--space-6);
  color: var(--color-text-muted);
}

.onboarding__error {
  margin-bottom: var(--space-4);
  color: var(--color-danger);
}

.onboarding__counter {
  display: inline-flex;
  align-items: center;
  gap: var(--space-3);
  font-weight: 600;
  color: var(--color-text);
}

.onboarding__slots {
  display: inline-flex;
  gap: var(--space-1);
}

.onboarding__slot {
  width: 10px;
  height: 10px;
  border: 1.5px solid var(--color-primary);
  border-radius: 50%;
  transition: background-color var(--duration-fast) var(--ease-standard);
}

.onboarding__slot--filled {
  background: var(--color-primary);
}

.onboarding__skeleton {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.onboarding__skeleton-title {
  flex-basis: 100%;
  height: 2.5rem;
  margin-bottom: var(--space-5);
  border-radius: var(--radius-sm);
  background: var(--color-surface-muted);
}

.onboarding__skeleton-chip {
  width: calc(96px + (var(--space-6) * 1));
  height: 44px;
  border-radius: var(--radius-pill);
  background: var(--color-surface-muted);
}

.onboarding__skeleton-chip:nth-child(3n) {
  width: 180px;
}

@media (min-width: 600px) {
  .onboarding__topbar {
    padding-block: var(--space-4);
  }

  .onboarding__step {
    padding-top: var(--space-6);
  }
}

@media (prefers-reduced-motion: no-preference) {
  .onboarding__skeleton > * {
    animation: pulse 1.2s ease-in-out infinite alternate;
  }

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
