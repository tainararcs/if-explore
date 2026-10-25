<!-- Progresso do onboarding: dois segmentos obrigatórios e um tracejado quando o refinamento está aberto. -->
<template>
  <div class="onboarding-progress">
    <div
      class="onboarding-progress__bar"
      aria-hidden="true"
    >
      <span
        v-for="segment in segments"
        :key="segment.step"
        class="onboarding-progress__segment"
        :class="{
          'onboarding-progress__segment--done': segment.done,
          'onboarding-progress__segment--optional': segment.step === 'genres',
        }"
      />
    </div>
    <p class="onboarding-progress__label">
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
</script>

<style scoped>
.onboarding-progress {
  display: flex;
  flex: 1;
  align-items: center;
  gap: var(--space-3);
  min-width: 0;
}

.onboarding-progress__bar {
  display: flex;
  flex: 1;
  gap: var(--space-1);
  max-width: 240px;
}

.onboarding-progress__segment {
  flex: 1;
  height: 4px;
  border-radius: var(--radius-pill);
  background: var(--color-border);
  transition: background-color var(--duration-base) var(--ease-standard);
}

.onboarding-progress__segment--done {
  background: var(--color-primary);
}

.onboarding-progress__segment--optional {
  background: repeating-linear-gradient(
    90deg,
    var(--color-primary) 0 6px,
    transparent 6px 10px
  );
}

.onboarding-progress__label {
  flex-shrink: 0;
  font-size: var(--text-small);
  color: var(--color-text-muted);
}
</style>
