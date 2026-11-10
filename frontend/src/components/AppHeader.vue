<!--
  Cabeçalho da aplicação: a marca leva às boas-vindas; a navegação principal mostra
  as duas formas de achar um livro, "Para você" (recomendações) e "Pergunte à IA",
  como abas; o menu de três linhas reúne preferências, tema e "Sobre".
  A partir de 600px as abas ficam centralizadas na mesma linha; abaixo disso ocupam
  uma segunda linha, de largura total, sempre visível.
-->
<template>
  <header
    class="app-header z-20 bg-surface"
    :class="sticky ? 'sticky top-0' : 'relative'"
  >
    <!--
      Celular: marca e menu na primeira linha, abas na segunda.
      A partir de 600px: três colunas, com as abas no centro.
    -->
    <div class="container grid grid-cols-[1fr_auto] items-center gap-x-2 sm:min-h-(--header-height) sm:grid-cols-[1fr_auto_1fr] sm:gap-x-4">
      <RouterLink
        class="inline-flex min-h-(--header-height) items-center gap-3 justify-self-start whitespace-nowrap text-text no-underline sm:min-h-11"
        to="/"
        :aria-label="t('common.brandHomeLabel')"
      >
        <BrandMark />
        <span class="font-display text-[1.25rem] leading-none">{{ t('common.appName') }}</span>
      </RouterLink>

      <nav
        :aria-label="t('common.nav.label')"
        class="col-span-2 row-start-2 pb-3 sm:col-span-1 sm:col-start-2 sm:row-start-1 sm:pb-0"
      >
        <!-- No celular, as duas abas dividem um trilho de largura total. -->
        <ul class="m-0 grid list-none grid-cols-2 gap-1 rounded-pill bg-surface-muted p-1 sm:flex sm:bg-transparent sm:p-0">
          <li
            v-for="tab in tabs"
            :key="tab.id"
          >
            <RouterLink
              v-slot="{ href, navigate }"
              :to="tab.to"
              custom
            >
              <!--
                O destaque da aba atual é um elemento à parte, sob o rótulo: na troca de
                aba ele desliza até a outra posição (view-transition-name em index.css),
                enquanto os rótulos ficam parados e só trocam de cor.
              -->
              <a
                :href="href"
                class="relative flex min-h-11 items-center justify-center whitespace-nowrap rounded-pill px-4 text-small font-semibold text-text-muted no-underline hover:text-text sm:hover:bg-surface-muted aria-[current=page]:text-on-primary-soft"
                :aria-current="tab.isCurrent ? 'page' : undefined"
                @click="navigate"
              >
                <span
                  v-if="tab.isCurrent"
                  class="header-tab-indicator absolute inset-0 rounded-pill bg-primary-soft"
                  aria-hidden="true"
                />
                <span
                  class="relative flex items-center gap-2"
                  :class="`header-tab-label--${tab.id}`"
                >
                  <component
                    :is="tab.icon"
                    class="size-5 shrink-0 text-primary"
                  />
                  {{ tab.label }}
                </span>
              </a>
            </RouterLink>
          </li>
        </ul>
      </nav>

      <!--
        A margem negativa compensa o respiro interno do botão (44px com ícone de 24px),
        alinhando o ícone à margem como a marca à esquerda.
      -->
      <div class="-me-2.5 justify-self-end sm:col-start-3 sm:row-start-1">
        <HeaderMenu />
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, type Component } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute, type RouteLocationRaw } from 'vue-router'
import { useReadingPreferences } from '../composables/useReadingPreferences'
import { tabIndexOf } from '../lib/tab-transition'
import BrandMark from './BrandMark.vue'
import HeaderMenu from './HeaderMenu.vue'
import IconLibrary from './icons/IconLibrary.vue'
import IconSparkle from './icons/IconSparkle.vue'

interface Props {
  /** Mantém o cabeçalho fixo no topo durante a rolagem. */
  sticky?: boolean
}

interface HeaderTab {
  id: string
  label: string
  icon: Component
  to: RouteLocationRaw
  isCurrent: boolean
}

withDefaults(defineProps<Props>(), {
  sticky: false,
})

const { t } = useI18n()
const route = useRoute()
const { hasPreferences } = useReadingPreferences()

/**
 * As duas abas. A aba ativa segue o caminho, não a query (o Vue Router não a
 * compara ao marcar o link exato), por isso os links são `custom`.
 */
const tabs = computed<HeaderTab[]>(() => {
  const { q } = route.query
  return [
    {
      id: 'for-you',
      label: t('common.nav.forYou'),
      icon: IconLibrary,
      // Sem preferências não há recomendações (a rota /home volta às boas-vindas):
      // a aba leva ao onboarding, que é o começo desse caminho.
      to: hasPreferences.value ? '/home' : '/onboarding',
      isCurrent: tabIndexOf(route.path) === 0,
    },
    {
      id: 'discover',
      label: t('common.nav.discover'),
      icon: IconSparkle,
      // Na home, o texto da busca vai junto como ponto de partida do pedido.
      to: {
        path: '/discover',
        query: route.path === '/home' && typeof q === 'string' && q ? { q } : {},
      },
      isCurrent: tabIndexOf(route.path) === 1,
    },
  ]
})
</script>
