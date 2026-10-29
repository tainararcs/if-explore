<!-- Tela de boas-vindas: apresenta o projeto e inicia a descoberta de leituras ou leva às recomendações salvas. -->
<template>
  <div class="flex min-h-dvh flex-col">
    <AppHeader />

    <!-- As capas giradas do leque não podem gerar rolagem horizontal. -->
    <main class="flex-1 overflow-x-clip">
      <section
        class="container grid gap-12 pt-8 pb-12 md:min-h-[min(100dvh-var(--header-height),720px)] md:grid-cols-[minmax(0,560px)_minmax(0,1fr)] md:items-center md:py-16"
        aria-labelledby="welcome-title"
      >
        <div class="welcome__intro flex flex-col items-start">
          <!-- Filete abaixo do sobretítulo, como no moodboard. -->
          <p class="eyebrow after:mt-4 after:block after:h-px after:w-12 after:bg-primary after:content-['']">
            {{ t('welcome.eyebrow') }}
          </p>
          <h1
            id="welcome-title"
            class="mt-4 text-display leading-[1.05]"
          >
            <Translation
              keypath="welcome.title"
              scope="global"
            >
              <template #emphasis>
                <em class="text-primary">{{ t('welcome.titleEmphasis') }}</em>
              </template>
            </Translation>
          </h1>
          <p class="mt-6 max-w-[52ch] text-[1.0625rem] text-text-muted">
            {{ t('welcome.lead') }}
          </p>

          <div class="mt-8 flex flex-col gap-3 self-stretch sm:flex-row sm:flex-wrap sm:self-start">
            <template v-if="hasPreferences">
              <RouterLink
                class="button button--primary"
                to="/home"
              >
                {{ t('welcome.viewRecommendations') }}
                <span class="button__arrow"><IconArrowRight /></span>
              </RouterLink>
              <RouterLink
                class="button button--secondary"
                to="/onboarding"
              >
                {{ t('welcome.restart') }}
              </RouterLink>
            </template>
            <RouterLink
              v-else
              class="button button--primary"
              to="/onboarding"
            >
              {{ t('welcome.start') }}
              <span class="button__arrow"><IconArrowRight /></span>
            </RouterLink>
          </div>

          <p class="mt-4 text-small text-text-muted">
            {{ t('welcome.privacy') }}
          </p>
        </div>

        <WelcomeCoverFan
          :books="fanBooks"
        />
      </section>

      <WelcomeHowItWorks />
    </main>

    <footer class="border-t border-border py-6 text-small text-text-muted">
      <div class="container flex flex-col gap-2 md:flex-row md:items-center md:justify-between">
        <p>{{ t('common.libraryName') }} · {{ t('common.institution') }}</p>
        <a
          :href="LIBRARY_CATALOG_URL"
          target="_blank"
          rel="noopener noreferrer"
          class="inline-flex min-h-11 items-center gap-1 font-semibold"
        >
          {{ t('common.officialSite') }}
          <IconExternalLink class="size-4" />
          <span class="sr-only">{{ t('common.opensInNewTab') }}</span>
        </a>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { Translation, useI18n } from 'vue-i18n'
import AppHeader from '../../../components/AppHeader.vue'
import IconArrowRight from '../../../components/icons/IconArrowRight.vue'
import IconExternalLink from '../../../components/icons/IconExternalLink.vue'
import { useReadingPreferences } from '../../../composables/useReadingPreferences'
import { LIBRARY_CATALOG_URL } from '../../../lib/library-catalog'
import type { Book } from '../../../models/book'
import { getBooksByIds } from '../../../services/catalog-service'
import WelcomeCoverFan from '../components/WelcomeCoverFan.vue'
import WelcomeHowItWorks from '../components/WelcomeHowItWorks.vue'

// Seleção fixa para uma composição estável, misturando áreas e literatura.
const FAN_BOOK_IDS = [
  'darwin-origem-especies',
  'machado-dom-casmurro',
  'rosa-grande-sertao',
  'martin-codigo-limpo',
  'freire-pedagogia-oprimido',
]

const { t } = useI18n()
const { hasPreferences } = useReadingPreferences()

const fanBooks = ref<Book[]>([])

onMounted(async () => {
  try {
    fanBooks.value = await getBooksByIds(FAN_BOOK_IDS)
  } catch {
    // A ilustração é decorativa; sem capas a tela continua completa.
    fanBooks.value = []
  }
})
</script>

<style scoped>
/* Entrada em cascata dos textos; os atrasos dependem da posição de cada filho. */
@media (prefers-reduced-motion: no-preference) {
  .welcome__intro > * {
    animation: rise-in 400ms var(--ease-standard) both;
  }

  .welcome__intro > :nth-child(2) {
    animation-delay: 60ms;
  }

  .welcome__intro > :nth-child(3) {
    animation-delay: 120ms;
  }

  .welcome__intro > :nth-child(n + 4) {
    animation-delay: 180ms;
  }
}

@keyframes rise-in {
  from {
    opacity: 0;
    transform: translateY(var(--space-3));
  }
}
</style>
