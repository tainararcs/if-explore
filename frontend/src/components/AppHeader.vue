<!--
  Cabeçalho da aplicação: a marca leva às boas-vindas, a navegação principal
  ("Recomendações" e "Sobre"), o botão em destaque da descoberta com IA e um
  espaço para ações contextuais da tela.
  A partir de 600px os links ficam centralizados; abaixo disso vão para um
  menu em tela cheia (abaixo do cabeçalho), aberto pelo botão de três linhas.
-->
<template>
  <header
    ref="header"
    class="z-20 bg-surface"
    :class="sticky ? 'sticky top-0' : 'relative'"
  >
    <!-- Três colunas: marca à esquerda, links de texto centralizados e ações em ícone à direita. -->
    <div class="container grid min-h-(--header-height) grid-cols-[auto_1fr] items-center gap-2 sm:grid-cols-[1fr_auto_1fr] sm:gap-4">
      <RouterLink
        class="inline-flex min-h-11 items-center gap-3 justify-self-start whitespace-nowrap text-text no-underline"
        to="/"
        :aria-label="t('common.brandHomeLabel')"
      >
        <BrandMark />
        <span class="font-display text-[1.25rem] leading-none">{{ t('common.appName') }}</span>
      </RouterLink>

      <!--
        No celular, o mesmo <nav> vira um painel fixo que ocupa a tela abaixo do
        cabeçalho, com os links e um rodapé simples.
      -->
      <nav
        :id="menuId"
        :aria-label="t('common.nav.label')"
        class="sm:block"
        :class="
          isMenuOpen
            ? 'max-sm:fixed max-sm:inset-x-0 max-sm:bottom-0 max-sm:flex max-sm:flex-col max-sm:overflow-y-auto max-sm:bg-surface max-sm:pt-4'
            : 'max-sm:hidden'
        "
        :style="isMenuOpen ? { top: `${menuTop}px` } : undefined"
      >
        <ul class="container m-0 flex list-none flex-col gap-1 p-0 sm:w-auto sm:flex-row sm:items-center sm:gap-2">
          <li>
            <RouterLink
              to="/home"
              class="header-link header-link--tracks-page relative flex min-h-12 items-center rounded-pill px-3 text-h3 font-semibold text-text-muted no-underline hover:text-text max-sm:hover:bg-surface-muted aria-[current=page]:text-primary max-sm:aria-[current=page]:underline max-sm:aria-[current=page]:decoration-2 max-sm:aria-[current=page]:underline-offset-[6px] sm:inline-flex sm:min-h-11 sm:text-small"
              @click="isMenuOpen = false"
            >
              {{ t('common.nav.recommendations') }}
            </RouterLink>
          </li>
          <li>
            <RouterLink
              to="/#about-section"
              class="header-link relative flex min-h-12 items-center rounded-pill px-3 text-h3 font-semibold text-text-muted no-underline hover:text-text max-sm:hover:bg-surface-muted sm:inline-flex sm:min-h-11 sm:text-small"
              @click="isMenuOpen = false"
            >
              {{ t('common.nav.about') }}
            </RouterLink>
          </li>
        </ul>

        <div class="container mt-auto flex flex-col gap-1 border-t border-border px-3 py-6 text-small text-text-muted sm:hidden">
          <p>{{ t('common.libraryName') }}</p>
          <p>{{ t('common.institution') }}</p>
          <a
            :href="LIBRARY_CATALOG_URL"
            target="_blank"
            rel="noopener noreferrer"
            class="mt-2 inline-flex min-h-11 items-center gap-1 self-start font-semibold"
          >
            {{ t('common.officialSite') }}
            <IconExternalLink class="size-4" />
            <span class="sr-only">{{ t('common.opensInNewTab') }}</span>
          </a>
        </div>
      </nav>

      <!--
        No celular, a margem negativa compensa o respiro interno dos botões (44px com
        ícone de 24px), alinhando o último ícone à margem como a marca à esquerda.
      -->
      <div class="-me-2.5 flex items-center gap-1 justify-self-end sm:me-0 sm:gap-2">
        <!--
          Descoberta com IA, a ação principal do cabeçalho: botão preenchido com rótulo a
          partir de 900px e só com o ícone abaixo disso. Some na própria tela da descoberta.
        -->
        <RouterLink
          v-if="route.path !== '/discover'"
          class="button button--primary button--small max-md:size-11 max-md:min-h-11 max-md:p-0"
          :to="discoverLink"
          :title="t('common.discover.label')"
        >
          <IconSparkle class="size-5 shrink-0" />
          <!-- Abaixo de 900px o rótulo some da tela, mas continua sendo o nome do botão. -->
          <span class="max-md:sr-only">{{ t('common.discover.action') }}</span>
        </RouterLink>
        <slot name="actions" />
        <ThemeToggle />
        <button
          ref="menuButton"
          type="button"
          class="grid size-11 cursor-pointer place-items-center rounded-[50%] border-0 bg-transparent p-0 text-text hover:bg-surface-muted sm:hidden"
          :aria-label="isMenuOpen ? t('common.nav.closeMenu') : t('common.nav.openMenu')"
          :aria-expanded="isMenuOpen"
          :aria-controls="menuId"
          @click="isMenuOpen = !isMenuOpen"
        >
          <IconClose
            v-if="isMenuOpen"
            class="size-6"
          />
          <IconMenu
            v-else
            class="size-6"
          />
        </button>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { computed, ref, useId, useTemplateRef, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { LIBRARY_CATALOG_URL } from '../lib/library-catalog'
import BrandMark from './BrandMark.vue'
import IconClose from './icons/IconClose.vue'
import IconExternalLink from './icons/IconExternalLink.vue'
import IconMenu from './icons/IconMenu.vue'
import IconSparkle from './icons/IconSparkle.vue'
import ThemeToggle from './ThemeToggle.vue'

interface Props {
  /** Mantém o cabeçalho fixo no topo durante a rolagem. */
  sticky?: boolean
}

withDefaults(defineProps<Props>(), {
  sticky: false,
})

defineSlots<{
  actions?: () => unknown
}>()

const { t } = useI18n()
const route = useRoute()
const menuId = useId()
const header = useTemplateRef<HTMLElement>('header')
const menuButton = useTemplateRef<HTMLButtonElement>('menuButton')

// Na home, o texto da busca vai junto como ponto de partida do pedido.
const discoverLink = computed(() => {
  const { q } = route.query
  return { path: '/discover', query: route.path === '/home' && typeof q === 'string' && q ? { q } : {} }
})

const isMenuOpen = ref(false)
// Posição do painel: logo abaixo do cabeçalho, onde quer que ele esteja na tela.
const menuTop = ref(0)

// Navegar fecha o menu.
watch(
  () => route.fullPath,
  () => {
    isMenuOpen.value = false
  },
)

function closeOnOutsidePointer(event: PointerEvent): void {
  if (event.target instanceof Node && !header.value?.contains(event.target)) {
    isMenuOpen.value = false
  }
}

// Esc fecha o menu e devolve o foco ao botão que o abriu.
function closeOnEscape(event: KeyboardEvent): void {
  if (event.key === 'Escape') {
    isMenuOpen.value = false
    menuButton.value?.focus()
  }
}

// Enquanto o menu está aberto, a página atrás não rola e os ouvintes globais existem;
// a limpeza também roda quando o cabeçalho sai da tela.
watch(isMenuOpen, (open, _previous, onCleanup) => {
  if (!open) {
    return
  }
  menuTop.value = header.value?.getBoundingClientRect().bottom ?? 0
  document.body.style.overflow = 'hidden'
  document.addEventListener('pointerdown', closeOnOutsidePointer)
  document.addEventListener('keydown', closeOnEscape)
  onCleanup(() => {
    document.body.style.overflow = ''
    document.removeEventListener('pointerdown', closeOnOutsidePointer)
    document.removeEventListener('keydown', closeOnEscape)
  })
})
</script>

<style scoped>
/*
 * Sublinhado dos links no desktop: nasce no centro e ultrapassa o texto em 4px de cada lado.
 * O estado ativo fica restrito a --tracks-page porque o Vue Router ignora o hash ao marcar
 * aria-current, o que deixaria "Sobre" (/#about-section) sublinhado na tela de boas-vindas.
 * A animação usa left/right, e não scaleX: a camada criada pelo transform suaviza as bordas
 * e deixa o traço visualmente mais grosso enquanto anima.
 */
@media (min-width: 600px) {
  .header-link::after {
    position: absolute;
    right: 50%;
    bottom: 6px;
    left: 50%;
    height: 2px;
    border-radius: var(--radius-pill);
    background: currentColor;
    content: '';
  }

  .header-link:focus-visible::after,
  .header-link--tracks-page[aria-current='page']::after {
    right: var(--space-2);
    left: var(--space-2);
  }
}

@media (min-width: 600px) and (hover: hover) {
  .header-link:hover::after {
    right: var(--space-2);
    left: var(--space-2);
  }
}

@media (min-width: 600px) and (prefers-reduced-motion: no-preference) {
  .header-link::after {
    transition:
      left var(--duration-base) var(--ease-standard),
      right var(--duration-base) var(--ease-standard);
  }
}
</style>
