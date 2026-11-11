<!--
  Espera pelas sugestões: mensagens em sequência sobre o que está acontecendo
  (a IA leva alguns segundos) e cards provisórios no formato dos resultados.
-->
<template>
  <div
    class="grid gap-4"
    role="status"
  >
    <!-- Leitores de tela ouvem uma única mensagem; as etapas são só visuais. -->
    <span class="sr-only">{{ t('discovery.loading') }}</span>
    <p
      class="m-0 flex items-center gap-2 font-semibold text-primary"
      aria-hidden="true"
    >
      <IconSparkle class="discovery-loading__icon size-5 shrink-0" />
      <Transition
        name="discovery-step"
        mode="out-in"
      >
        <span :key="step">{{ t(`discovery.loadingSteps.${STEP_KEYS[step]}`) }}</span>
      </Transition>
    </p>
    <div
      class="grid gap-4"
      aria-hidden="true"
    >
      <div
        v-for="item in 3"
        :key="item"
        class="grid grid-cols-[88px_minmax(0,1fr)] gap-4 rounded-md border border-border bg-surface p-3 sm:p-4"
      >
        <span class="discovery-loading__pulse aspect-[2/3] rounded-cover bg-surface-muted" />
        <div class="flex flex-col gap-2">
          <span class="discovery-loading__pulse h-6 w-4/5 rounded-sm bg-surface-muted" />
          <span class="discovery-loading__pulse h-4 w-1/2 rounded-sm bg-surface-muted" />
          <span class="discovery-loading__pulse mt-3 h-12 w-full rounded-sm bg-surface-muted" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import IconSparkle from '../../../components/icons/IconSparkle.vue'

const STEP_KEYS = ['read', 'search', 'choose', 'explain'] as const
const STEP_MS = 1200

const { t } = useI18n()

// Avança uma etapa a cada pouco e para na última, mesmo que a resposta demore mais.
const step = ref(0)
let timer: number | undefined

onMounted(() => {
  timer = window.setInterval(() => {
    if (step.value < STEP_KEYS.length - 1) {
      step.value += 1
    } else {
      window.clearInterval(timer)
    }
  }, STEP_MS)
})

onUnmounted(() => window.clearInterval(timer))
</script>

<style scoped>
@media (prefers-reduced-motion: no-preference) {
  .discovery-loading__pulse {
    animation: pulse 1.2s ease-in-out infinite alternate;
  }

  .discovery-loading__icon {
    animation: spin 2.4s linear infinite;
  }

  .discovery-step-enter-active,
  .discovery-step-leave-active {
    transition:
      opacity var(--duration-fast) var(--ease-standard),
      transform var(--duration-fast) var(--ease-standard);
  }

  .discovery-step-enter-from {
    opacity: 0;
    transform: translateY(4px);
  }

  .discovery-step-leave-to {
    opacity: 0;
    transform: translateY(-4px);
  }
}

@keyframes pulse {
  to {
    opacity: 0.5;
  }
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
