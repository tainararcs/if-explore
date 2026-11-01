<!-- Explica em três passos como o IF Explore gera as recomendações. -->
<template>
  <section
    class="bg-bg py-12 md:py-16"
    aria-labelledby="how-it-works-title"
    style="background-color: light-dark(#E5E0D2, #141713)"
  >
    <div class="container">
      <h2 id="how-it-works-title">
        {{ t('welcome.howItWorks.title') }}
      </h2>
      <ol class="mt-6 grid list-none gap-6 p-0 md:mt-8 md:grid-cols-3 md:gap-8">
        <li
          v-for="(step, index) in steps"
          :key="step.key"
          class="flex items-start gap-4"
        >
          <span
            class="how-it-works__icon grid size-12 shrink-0 place-items-center rounded-[50%] bg-primary-soft text-on-primary-soft"
          >
            <component :is="step.icon" />
          </span>
          <div>
            <p class="eyebrow">
              {{ String(index + 1).padStart(2, '0') }}
            </p>
            <h3>{{ t(`welcome.howItWorks.${step.key}.title`) }}</h3>
            <p class="mt-1 text-text-muted">
              {{ t(`welcome.howItWorks.${step.key}.text`) }}
            </p>
          </div>
        </li>
      </ol>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import IconBookmark from '../../../components/icons/IconBookmark.vue'
import IconLibrary from '../../../components/icons/IconLibrary.vue'
import IconSparkle from '../../../components/icons/IconSparkle.vue'

const { t } = useI18n()

const steps = [
  { key: 'areas', icon: IconLibrary },
  { key: 'books', icon: IconBookmark },
  { key: 'recommendations', icon: IconSparkle },
]
</script>

<style scoped>
:global(:root[data-theme='light']) .how-it-works__icon {
  color: var(--color-primary-hover);
}

@media (prefers-color-scheme: light) {
  :global(:root:not([data-theme])) .how-it-works__icon {
    color: var(--color-primary-hover);
  }
}
</style>
