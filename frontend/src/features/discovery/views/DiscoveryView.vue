<!-- Descoberta com IA: o visitante descreve o que quer ler e recebe títulos do acervo com o motivo de cada um. -->
<template>
  <div class="flex min-h-dvh flex-col">
    <AppHeader sticky />

    <main class="container flex-1 pt-3 pb-16 md:pt-4">
      <RouterLink
        class="button button--ghost button--small -ms-3 px-3"
        :to="backPath"
      >
        <IconArrowLeft class="size-5" />
        {{ hasPreferences ? t('discovery.back') : t('discovery.backStart') }}
      </RouterLink>

      <div class="mx-auto mt-4 max-w-[720px] md:mt-8">
        <p class="eyebrow">
          {{ t('discovery.eyebrow') }}
        </p>
        <h1 class="mt-2">
          {{ t('discovery.title') }}
        </h1>
        <p class="mt-2 max-w-[60ch] text-text-muted">
          {{ t('discovery.lead') }}
        </p>

        <DiscoveryForm
          v-model:query="input"
          v-model:use-preferences="usePreferences"
          class="mt-6"
          :can-submit="canSubmit && !isLoading"
          :is-loading="isLoading"
          :show-preference-toggle="hasPreferences"
          @submit="submit"
        />
      </div>

      <section
        class="mx-auto mt-10 max-w-[720px] md:mt-12"
        aria-live="polite"
        :aria-busy="isLoading"
        :aria-label="t('discovery.resultsLabel')"
      >
        <div
          v-if="state.status === 'loading'"
          class="grid gap-4"
          role="status"
        >
          <span class="sr-only">{{ t('discovery.loading') }}</span>
          <div
            v-for="item in 3"
            :key="item"
            class="grid grid-cols-[88px_minmax(0,1fr)] gap-4 rounded-md border border-border bg-surface p-3 sm:grid-cols-[104px_minmax(0,1fr)] sm:gap-5 sm:p-4"
            aria-hidden="true"
          >
            <span class="discovery__pulse aspect-[2/3] rounded-cover bg-surface-muted" />
            <div class="flex flex-col gap-2">
              <span class="discovery__pulse h-6 w-4/5 rounded-sm bg-surface-muted" />
              <span class="discovery__pulse h-4 w-1/2 rounded-sm bg-surface-muted" />
              <span class="discovery__pulse mt-3 h-12 w-full rounded-sm bg-surface-muted" />
            </div>
          </div>
        </div>

        <div
          v-else-if="state.status === 'error'"
          role="alert"
        >
          <p class="mb-4 text-danger">
            {{ state.rateLimited ? t('discovery.rateLimited') : t('discovery.error') }}
          </p>
          <button
            type="button"
            class="button button--secondary"
            @click="retry"
          >
            {{ t('discovery.retry') }}
          </button>
        </div>

        <template v-else-if="state.status === 'success'">
          <div
            v-if="state.result.items.length === 0"
            class="flex flex-col items-center gap-3 py-8 text-center"
          >
            <h2
              ref="resultsHeading"
              class="text-h2"
              tabindex="-1"
            >
              {{ t('discovery.emptyTitle') }}
            </h2>
            <p class="mb-2 max-w-[48ch] text-text-muted">
              {{ t('discovery.emptyText') }}
            </p>
            <RouterLink
              v-if="hasPreferences"
              class="button button--secondary"
              :to="{ path: '/home', query: { q: submittedQuery } }"
            >
              {{ t('discovery.emptyAction') }}
            </RouterLink>
          </div>

          <template v-else>
            <h2
              ref="resultsHeading"
              class="text-h2"
              tabindex="-1"
            >
              {{ t('discovery.resultsTitle', { query: submittedQuery }) }}
            </h2>
            <p
              v-if="state.result.source === 'rules'"
              class="mt-4 rounded-md bg-surface-muted p-4 text-small"
              role="status"
            >
              {{ t('discovery.fallback') }}
            </p>
            <p
              v-else-if="state.result.message"
              class="mt-2 text-text-muted"
            >
              {{ state.result.message }}
            </p>
            <ol class="m-0 mt-6 grid list-none gap-4 p-0">
              <li
                v-for="item in state.result.items"
                :key="item.book.id"
              >
                <DiscoveryResultItem :item="item" />
              </li>
            </ol>
            <p
              v-if="state.result.source === 'ai'"
              class="mt-6 text-caption text-text-muted"
            >
              {{ t('discovery.aiNote') }}
            </p>
          </template>
        </template>
      </section>
    </main>

    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, useTemplateRef, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import AppFooter from '../../../components/AppFooter.vue'
import AppHeader from '../../../components/AppHeader.vue'
import IconArrowLeft from '../../../components/icons/IconArrowLeft.vue'
import DiscoveryForm from '../components/DiscoveryForm.vue'
import DiscoveryResultItem from '../components/DiscoveryResultItem.vue'
import { useDiscovery } from '../composables/useDiscovery'

const { t } = useI18n()

const { input, usePreferences, hasPreferences, state, submittedQuery, canSubmit, isLoading, submit, retry } =
  useDiscovery()

const backPath = computed(() => (hasPreferences.value ? '/home' : '/'))

const resultsHeading = useTemplateRef<HTMLHeadingElement>('resultsHeading')

// Quando as sugestões chegam, o foco vai para o título delas, para quem navega pelo teclado ou leitor de tela.
watch(
  () => state.value.status,
  (status) => {
    if (status === 'success') {
      void nextTick(() => resultsHeading.value?.focus())
    }
  },
)
</script>

<style scoped>
@media (prefers-reduced-motion: no-preference) {
  .discovery__pulse {
    animation: pulse 1.2s ease-in-out infinite alternate;
  }
}

@keyframes pulse {
  to {
    opacity: 0.5;
  }
}
</style>
