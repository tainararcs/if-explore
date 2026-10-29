<!--
  Cabeçalho da aplicação: a marca leva às boas-vindas, a navegação principal
  ("Recomendações" e "Sobre") e um espaço para ações contextuais da tela.
  A partir de 600px os links ficam centralizados; abaixo disso vão para um
  menu em tela cheia (abaixo do cabeçalho), aberto pelo botão de três linhas.
-->
<template>
  <header
    ref="header"
    class="z-20 border-b border-border bg-surface"
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
              class="flex min-h-12 items-center rounded-pill px-3 text-h3 font-semibold text-text-muted no-underline hover:bg-surface-muted hover:text-text aria-[current=page]:text-primary aria-[current=page]:underline aria-[current=page]:decoration-2 aria-[current=page]:underline-offset-[6px] sm:inline-flex sm:min-h-11 sm:text-small"
              @click="isMenuOpen = false"
            >
              {{ t('common.nav.recommendations') }}
            </RouterLink>
          </li>
          <li>
            <!-- A página "Sobre" ainda não existe: o link aparece, mas fica desabilitado. -->
            <a
              role="link"
              aria-disabled="true"
              class="flex min-h-12 cursor-not-allowed items-center gap-2 rounded-pill px-3 text-h3 font-semibold text-text-muted no-underline sm:inline-flex sm:min-h-11 sm:text-small"
              :title="t('common.nav.comingSoon')"
            >
              <span>{{ t('common.nav.about') }}</span>
              <span class="rounded-pill bg-surface-muted px-2 py-0.5 text-caption">{{ t('common.nav.comingSoon') }}</span>
            </a>
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
import { ref, useId, useTemplateRef, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { LIBRARY_CATALOG_URL } from '../lib/library-catalog'
import BrandMark from './BrandMark.vue'
import IconClose from './icons/IconClose.vue'
import IconExternalLink from './icons/IconExternalLink.vue'
import IconMenu from './icons/IconMenu.vue'
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
