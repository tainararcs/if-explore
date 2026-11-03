<!-- Progresso do onboarding: um segmento por passo, preenchido até o passo atual. -->
<template>
  <div class="flex min-w-0 flex-1 items-center gap-3">
    <div
      class="flex max-w-60 flex-1 gap-1"
      aria-hidden="true"
    >
      <span
        v-for="segment in segments"
        :key="segment.step"
        class="h-1 flex-1 rounded-pill transition-[background-color] duration-(--duration-base) ease-standard"
        :class="segment.done ? 'bg-primary' : 'bg-border'"
      />
    </div>
    <p class="shrink-0 text-small text-text-muted">
      {{
        t('onboarding.progress.step', {
          current: stepIndex(step) + 1,
          total: ONBOARDING_STEPS.length,
        })
      }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { ONBOARDING_STEPS, stepIndex, type OnboardingStep } from '../models/onboarding-draft'

interface Props {
  step: OnboardingStep
}

const props = defineProps<Props>()

const { t } = useI18n()

const segments = computed(() =>
  ONBOARDING_STEPS.map((step) => ({
    step,
    done: stepIndex(step) <= stepIndex(props.step),
  })),
)
</script>
