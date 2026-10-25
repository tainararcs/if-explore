<!-- Explica em três passos como o IF Explore gera as recomendações. -->
<template>
  <section
    class="how-it-works"
    aria-labelledby="how-it-works-title"
  >
    <div class="container">
      <h2 id="how-it-works-title">
        {{ t('welcome.howItWorks.title') }}
      </h2>
      <ol class="how-it-works__steps">
        <li
          v-for="(step, index) in steps"
          :key="step.key"
          class="how-it-works__step"
        >
          <span class="how-it-works__icon">
            <component :is="step.icon" />
          </span>
          <div>
            <p class="eyebrow">
              {{ String(index + 1).padStart(2, '0') }}
            </p>
            <h3>{{ t(`welcome.howItWorks.${step.key}.title`) }}</h3>
            <p class="how-it-works__text">
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
.how-it-works {
  padding-block: var(--space-7);
  background: var(--color-surface);
  border-top: 1px solid var(--color-border);
}

.how-it-works__steps {
  display: grid;
  gap: var(--space-5);
  margin-top: var(--space-5);
  padding: 0;
  list-style: none;
}

.how-it-works__step {
  display: flex;
  align-items: flex-start;
  gap: var(--space-4);
}

.how-it-works__icon {
  display: grid;
  place-items: center;
  flex-shrink: 0;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: var(--color-primary-soft);
  color: var(--color-primary);
}

.how-it-works__text {
  margin-top: var(--space-1);
  color: var(--color-text-muted);
}

@media (min-width: 900px) {
  .how-it-works {
    padding-block: var(--space-8);
  }

  .how-it-works__steps {
    grid-template-columns: repeat(3, 1fr);
    gap: var(--space-6);
    margin-top: var(--space-6);
  }
}
</style>
