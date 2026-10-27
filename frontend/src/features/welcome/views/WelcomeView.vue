<!-- Tela de boas-vindas: apresenta o projeto e inicia a descoberta de leituras ou leva às recomendações salvas. -->
<template>
  <div class="welcome">
    <AppHeader />

    <main>
      <section
        class="welcome__hero container"
        aria-labelledby="welcome-title"
      >
        <div class="welcome__intro">
          <p class="eyebrow welcome__eyebrow">
            {{ t('welcome.eyebrow') }}
          </p>
          <h1
            id="welcome-title"
            class="welcome__title"
          >
            <Translation
              keypath="welcome.title"
              scope="global"
            >
              <template #emphasis>
                <em>{{ t('welcome.titleEmphasis') }}</em>
              </template>
            </Translation>
          </h1>
          <p class="welcome__lead">
            {{ t('welcome.lead') }}
          </p>

          <div class="welcome__actions">
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

          <p class="welcome__privacy">
            {{ t('welcome.privacy') }}
          </p>
        </div>

        <WelcomeCoverFan
          class="welcome__fan"
          :books="fanBooks"
        />
      </section>

      <WelcomeHowItWorks />
    </main>

    <footer class="welcome__footer">
      <div class="welcome__footer-inner container">
        <p>{{ t('common.libraryName') }} · {{ t('common.institution') }}</p>
        <a
          :href="LIBRARY_SITE_URL"
          target="_blank"
          rel="noopener noreferrer"
          class="welcome__external"
        >
          {{ t('welcome.officialSite') }}
          <IconExternalLink class="welcome__external-icon" />
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
import type { Book } from '../../../models/book'
import { getBooksByIds } from '../../../services/catalog-service'
import WelcomeCoverFan from '../components/WelcomeCoverFan.vue'
import WelcomeHowItWorks from '../components/WelcomeHowItWorks.vue'

const LIBRARY_SITE_URL =
  'https://biblioteca.barbacena.ifsudestemg.edu.br/cgi-bin/wxis.exe?IsisScript=phl82.xis&cipar=phl82.cip&lang=por'

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
.welcome {
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
}

.welcome main {
  flex: 1;
  /* As capas giradas do leque não podem gerar rolagem horizontal. */
  overflow-x: clip;
}

.welcome__hero {
  display: grid;
  gap: var(--space-7);
  padding-block: var(--space-6) var(--space-7);
}

.welcome__intro {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}

/* Filete abaixo do sobretítulo, como no moodboard. */
.welcome__eyebrow::after {
  content: '';
  display: block;
  width: 48px;
  height: 1px;
  margin-top: var(--space-4);
  background: var(--color-primary);
}

.welcome__title {
  margin-top: var(--space-4);
  font-size: var(--text-display);
  line-height: 1.05;
}

.welcome__title em {
  color: var(--color-primary);
}

.welcome__lead {
  max-width: 52ch;
  margin-top: var(--space-5);
  font-size: 1.0625rem;
  color: var(--color-text-muted);
}

.welcome__actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  align-self: stretch;
  margin-top: var(--space-6);
}

.welcome__privacy {
  margin-top: var(--space-4);
  font-size: var(--text-small);
  color: var(--color-text-muted);
}

.welcome__footer {
  padding-block: var(--space-5);
  border-top: 1px solid var(--color-border);
  font-size: var(--text-small);
  color: var(--color-text-muted);
}

.welcome__footer-inner {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.welcome__external {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  min-height: 44px;
  font-weight: 600;
}

.welcome__external-icon {
  width: 1rem;
  height: 1rem;
}

@media (min-width: 600px) {
  .welcome__actions {
    flex-direction: row;
    flex-wrap: wrap;
    align-self: flex-start;
  }
}

@media (min-width: 900px) {
  .welcome__hero {
    grid-template-columns: minmax(0, 560px) minmax(0, 1fr);
    align-items: center;
    min-height: min(100dvh - var(--header-height), 720px);
    padding-block: var(--space-8);
  }

  .welcome__footer-inner {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

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
