<!--
  Pergunte à IA: o visitante descreve o que quer ler e recebe títulos do acervo
  com o motivo de cada um. A partir de 900px, o pedido fica numa coluna fixa à
  esquerda e as sugestões ocupam o resto da largura; no celular, depois do envio,
  o formulário vira um resumo do pedido para que as sugestões apareçam logo.
-->
<template>
  <div class="flex min-h-dvh flex-col">
    <AppHeader sticky />

    <main class="container flex-1 pt-8 pb-16 md:pt-12">
      <p class="eyebrow">
        {{ t('discovery.eyebrow') }}
      </p>
      <h1 class="mt-2">
        {{ t('discovery.title') }}
      </h1>
      <p class="mt-2 max-w-[60ch] text-text-muted">
        {{ t('discovery.lead') }}
      </p>

      <div class="mt-6 grid grid-cols-[minmax(0,1fr)] gap-8 md:mt-8 md:grid-cols-[minmax(300px,340px)_minmax(0,1fr)] md:gap-10 lg:grid-cols-[380px_minmax(0,1fr)] lg:gap-12">
        <div class="discovery__aside md:sticky md:self-start">
          <DiscoveryQuerySummary
            v-if="isCollapsed"
            class="md:hidden"
            :query="submittedQuery"
            @edit="edit"
          />
          <div
            class="flex flex-col gap-6"
            :class="{ 'max-md:hidden': isCollapsed }"
          >
            <DiscoveryForm
              ref="form"
              v-model:query="input"
              v-model:use-preferences="usePreferences"
              :can-submit="canSubmit && !isLoading"
              :is-loading="isLoading"
              :show-preference-toggle="hasPreferences"
              @submit="send"
            />
            <DiscoveryStarters
              :recent="recentRequests"
              @repeat="repeat"
              @use-idea="useIdea"
              @clear-recent="clearRecent"
            />
          </div>
        </div>

        <section
          class="min-w-0"
          aria-live="polite"
          :aria-busy="isLoading"
          :aria-label="t('discovery.resultsLabel')"
        >
          <!-- Antes do primeiro pedido, o espaço das sugestões explica o que vai aparecer ali. -->
          <div
            v-if="state.status === 'idle'"
            class="flex flex-col gap-4 rounded-lg border border-dashed border-border-strong p-6 max-md:hidden lg:p-8"
          >
            <span class="grid size-12 place-items-center rounded-[50%] bg-primary-soft text-on-primary-soft">
              <IconSparkle />
            </span>
            <h2 class="m-0 text-h2">
              {{ t('discovery.intro.title') }}
            </h2>
            <ul class="m-0 grid max-w-[60ch] gap-3 p-0 ps-5 text-text-muted">
              <li>{{ t('discovery.intro.collection') }}</li>
              <li>{{ t('discovery.intro.reason') }}</li>
              <li>{{ t('discovery.intro.shelf') }}</li>
            </ul>
          </div>

          <DiscoveryLoading v-else-if="state.status === 'loading'" />

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
                class="text-h2 outline-none"
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
              <div class="flex flex-wrap items-start justify-between gap-x-4 gap-y-2">
                <h2
                  ref="resultsHeading"
                  class="m-0 min-w-0 text-h2 outline-none"
                  tabindex="-1"
                >
                  {{ t('discovery.resultsTitle', { query: submittedQuery }) }}
                </h2>
                <!-- A margem negativa alinha o texto do botão fantasma à margem, mesmo quando ele quebra de linha. -->
                <ShareButton
                  class="-mx-4 shrink-0"
                  small
                  :title="t('discovery.shareTitle')"
                  :text="t('discovery.shareText', { query: submittedQuery })"
                />
              </div>
              <p
                v-if="state.result.source === 'rules'"
                class="mt-4 rounded-md bg-surface-muted p-4 text-small"
                role="status"
              >
                {{ t('discovery.fallback') }}
              </p>
              <p
                v-else-if="state.result.message"
                class="mt-2 max-w-[65ch] text-text-muted"
              >
                {{ state.result.message }}
              </p>
              <ol class="m-0 mt-6 grid list-none gap-4 p-0">
                <li
                  v-for="item in state.result.items"
                  :key="item.book.id"
                >
                  <DiscoveryResultItem
                    :item="item"
                    :area-name="areaNames.get(item.book.areaId ?? '')"
                  />
                </li>
              </ol>

              <div class="mt-6 flex flex-col items-start gap-3">
                <button
                  v-if="canLoadMore"
                  type="button"
                  class="button button--secondary"
                  :disabled="moreStatus === 'loading'"
                  @click="loadMore"
                >
                  <IconSparkle class="size-5" />
                  {{ moreStatus === 'loading' ? t('discovery.more.loading') : t('discovery.more.action') }}
                </button>
                <p
                  v-if="moreStatus === 'loading'"
                  class="sr-only"
                  role="status"
                >
                  {{ t('discovery.more.loading') }}
                </p>
                <p
                  v-else-if="moreStatus === 'exhausted'"
                  class="m-0 text-small text-text-muted"
                  role="status"
                >
                  {{ t('discovery.more.exhausted') }}
                </p>
                <p
                  v-else-if="moreStatus === 'error' || moreStatus === 'rateLimited'"
                  class="m-0 text-small text-danger"
                  role="alert"
                >
                  {{ moreStatus === 'rateLimited' ? t('discovery.rateLimited') : t('discovery.more.error') }}
                </p>
              </div>

              <p
                v-if="state.result.source === 'ai'"
                class="mt-6 text-caption text-text-muted"
              >
                {{ t('discovery.aiNote') }}
              </p>
            </template>
          </template>
        </section>
      </div>
    </main>

    <AppFooter />
  </div>
</template>

<script setup lang="ts">
import { computed, nextTick, onMounted, ref, useTemplateRef, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import AppFooter from '../../../components/AppFooter.vue'
import AppHeader from '../../../components/AppHeader.vue'
import IconSparkle from '../../../components/icons/IconSparkle.vue'
import ShareButton from '../../../components/ShareButton.vue'
import type { KnowledgeArea } from '../../../models/taxonomy'
import { getKnowledgeAreas } from '../../../services/catalog-service'
import DiscoveryForm from '../components/DiscoveryForm.vue'
import DiscoveryLoading from '../components/DiscoveryLoading.vue'
import DiscoveryQuerySummary from '../components/DiscoveryQuerySummary.vue'
import DiscoveryResultItem from '../components/DiscoveryResultItem.vue'
import DiscoveryStarters from '../components/DiscoveryStarters.vue'
import { useDiscovery } from '../composables/useDiscovery'

const { t } = useI18n()

const {
  input,
  usePreferences,
  hasPreferences,
  state,
  moreStatus,
  recentRequests,
  submittedQuery,
  canSubmit,
  canLoadMore,
  isLoading,
  submit,
  submitText,
  retry,
  loadMore,
  clearRecent,
} = useDiscovery()

const form = useTemplateRef<InstanceType<typeof DiscoveryForm>>('form')
const resultsHeading = useTemplateRef<HTMLHeadingElement>('resultsHeading')

// No celular, depois de um pedido o formulário vira um resumo, até o visitante pedir para editar.
const isEditing = ref(false)
const isCollapsed = computed(() => state.value.status !== 'idle' && !isEditing.value)

// Nomes das áreas para os cards; sem eles, o card mostra só o ano.
const areas = ref<KnowledgeArea[]>([])
const areaNames = computed(() => new Map(areas.value.map((area) => [area.id, area.name])))

onMounted(() => {
  getKnowledgeAreas()
    .then((list) => {
      areas.value = list
    })
    .catch(() => undefined)
})

function send(): void {
  isEditing.value = false
  submit()
}

function repeat(request: string): void {
  isEditing.value = false
  submitText(request)
}

function useIdea(idea: string): void {
  input.value = idea
  form.value?.focus()
}

function edit(): void {
  isEditing.value = true
  void nextTick(() => form.value?.focus())
}

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
/*
  A partir de 900px, a coluna do pedido acompanha a rolagem logo abaixo do
  cabeçalho fixo; se for mais alta que a tela (muitos pedidos recentes), rola
  por dentro em vez de esconder o final.
*/
@media (min-width: 900px) {
  .discovery__aside {
    top: calc(var(--header-height) + var(--space-5));
    max-height: calc(100dvh - var(--header-height) - 2 * var(--space-5));
    overflow-x: hidden;
    overflow-y: auto;
  }
}
</style>
