<!-- Progresso do onboarding: dois segmentos obrigatórios e um tracejado quando o refinamento está aberto. -->
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
        :class="segmentClass(segment)"
      />
    </div>
    <p class="shrink-0 text-small text-text-muted">
      {{
        step === 'genres'
          ? t('onboarding.progress.refine')
          : t('onboarding.progress.step', { current: stepIndex(step) + 1, total: 2 })
      }}
    </p>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { stepIndex, type OnboardingStep } from '../models/onboarding-draft'

interface Props {
  step: OnboardingStep
}

const props = defineProps<Props>()

const { t } = useI18n()

const segments = computed(() => {
  const steps: OnboardingStep[] =
    props.step === 'genres' ? ['areas', 'books', 'genres'] : ['areas', 'books']
  return steps.map((step) => ({
    step,
    done: stepIndex(step) <= stepIndex(props.step),
  }))
})

// O segmento opcional (refinamento) é tracejado; os demais ficam cheios quando concluídos.
function segmentClass(segment: { step: OnboardingStep; done: boolean }): string {
  if (segment.step === 'genres') {
    return 'bg-[repeating-linear-gradient(90deg,var(--color-primary)_0_6px,transparent_6px_10px)]'
  }
  return segment.done ? 'bg-primary' : 'bg-border'
}
</script>
