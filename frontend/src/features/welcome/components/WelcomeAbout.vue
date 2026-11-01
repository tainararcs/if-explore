<!-- Apresenta brevemente a proposta e o público do projeto. -->
<template>
  <section
    id="about-section"
    class="bg-bg py-16 md:py-24"
    aria-labelledby="about-title"
  >
    <div class="container">
      <div class="grid gap-8 md:grid-cols-[minmax(0,0.9fr)_minmax(0,1.1fr)] md:items-end md:gap-16">
        <div>
          <p class="eyebrow text-primary">
            {{ t('welcome.about.eyebrow') }}
          </p>
          <h2
            id="about-title"
            class="mt-4 max-w-[15ch] text-h1"
          >
            {{ t('welcome.about.title') }}
          </h2>
        </div>
        <div class="max-w-[62ch]">
          <p class="text-[1.0625rem] leading-relaxed">
            {{ t('welcome.about.description') }}
          </p>
          <p class="mt-4 text-text-muted">
            {{ t('welcome.about.audience') }}
          </p>
          <RouterLink
            class="button button--primary mt-6"
            to="/onboarding"
          >
            {{ t('welcome.about.action') }}
          </RouterLink>
        </div>
      </div>

      <ul class="mt-12 grid list-none gap-4 p-0 md:mt-16 md:grid-cols-2 md:gap-6">
        <li class="rounded-lg bg-surface p-6 md:p-8">
          <h3 class="font-display text-h2">
            {{ t('welcome.about.discovery.title') }}
          </h3>
          <p class="mt-3 text-text-muted">
            {{ t('welcome.about.discovery.text') }}
          </p>
        </li>
        <li class="rounded-lg bg-surface p-6 md:p-8">
          <h3 class="font-display text-h2">
            {{ t('welcome.about.access.title') }}
          </h3>
          <p class="mt-3 text-text-muted">
            {{ t('welcome.about.access.text') }}
          </p>
        </li>
      </ul>
    </div>
  </section>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
</script>
