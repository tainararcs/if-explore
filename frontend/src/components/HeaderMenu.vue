<!--
  Menu do cabeçalho, aberto pelo botão de três linhas: ajustar (ou definir) as
  preferências de leitura, alternar o tema escuro e ir para "Sobre".
  É um painel de divulgação (botão com aria-expanded), não um menu ARIA: os itens
  são links e uma chave comuns, navegáveis com Tab. Fecha ao navegar, com Esc
  (o foco volta ao botão), com um toque fora ou quando o foco sai do painel.
-->
<template>
  <div
    ref="root"
    class="relative"
    @focusout="closeOnFocusLeave"
  >
    <button
      ref="toggleButton"
      type="button"
      class="grid size-11 cursor-pointer place-items-center rounded-[50%] border-0 bg-transparent p-0 text-text hover:bg-surface-muted"
      :class="{ 'bg-surface-muted': isOpen }"
      :aria-label="isOpen ? t('common.menu.close') : t('common.menu.open')"
      :aria-expanded="isOpen"
      :aria-controls="panelId"
      @click="isOpen = !isOpen"
    >
      <IconClose
        v-if="isOpen"
        class="size-6"
      />
      <IconMenu
        v-else
        class="size-6"
      />
    </button>

    <div
      v-show="isOpen"
      :id="panelId"
      class="absolute top-full right-0 mt-2 w-[min(18rem,calc(100vw-2*var(--gutter)))] rounded-md border border-border bg-surface p-1 shadow-md"
    >
      <ul class="m-0 flex list-none flex-col p-0">
        <li>
          <RouterLink
            :to="{ path: '/onboarding', query: { step: 'areas' } }"
            class="flex min-h-11 items-center gap-3 rounded-sm px-3 text-small font-semibold text-text no-underline hover:bg-surface-muted hover:text-text"
            @click="isOpen = false"
          >
            <IconAdjustments class="size-5 shrink-0 text-primary" />
            {{ hasPreferences ? t('common.adjustPreferences') : t('common.definePreferences') }}
          </RouterLink>
        </li>
        <li>
          <ThemeToggle />
        </li>
        <li class="mt-1 border-t border-border pt-1">
          <RouterLink
            to="/#about-section"
            class="flex min-h-11 items-center gap-3 rounded-sm px-3 text-small font-semibold text-text no-underline hover:bg-surface-muted hover:text-text"
            @click="isOpen = false"
          >
            <IconInfo class="size-5 shrink-0 text-primary" />
            {{ t('common.menu.about') }}
          </RouterLink>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, useId, useTemplateRef, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRoute } from 'vue-router'
import { useReadingPreferences } from '../composables/useReadingPreferences'
import IconAdjustments from './icons/IconAdjustments.vue'
import IconClose from './icons/IconClose.vue'
import IconInfo from './icons/IconInfo.vue'
import IconMenu from './icons/IconMenu.vue'
import ThemeToggle from './ThemeToggle.vue'

const { t } = useI18n()
const route = useRoute()
const { hasPreferences } = useReadingPreferences()
const panelId = useId()
const root = useTemplateRef<HTMLElement>('root')
const toggleButton = useTemplateRef<HTMLButtonElement>('toggleButton')

const isOpen = ref(false)

// Navegar fecha o menu.
watch(
  () => route.fullPath,
  () => {
    isOpen.value = false
  },
)

// Tab para fora do painel fecha o menu, sem roubar o foco de onde ele foi.
function closeOnFocusLeave(event: FocusEvent): void {
  if (!(event.relatedTarget instanceof Node) || !root.value?.contains(event.relatedTarget)) {
    isOpen.value = false
  }
}

function closeOnOutsidePointer(event: PointerEvent): void {
  if (event.target instanceof Node && !root.value?.contains(event.target)) {
    isOpen.value = false
  }
}

// Esc fecha o menu e devolve o foco ao botão que o abriu.
function closeOnEscape(event: KeyboardEvent): void {
  if (event.key === 'Escape') {
    isOpen.value = false
    toggleButton.value?.focus()
  }
}

// Os ouvintes globais só existem com o menu aberto e são removidos ao fechar ou desmontar.
watch(isOpen, (open, _previous, onCleanup) => {
  if (!open) {
    return
  }
  document.addEventListener('pointerdown', closeOnOutsidePointer)
  document.addEventListener('keydown', closeOnEscape)
  onCleanup(() => {
    document.removeEventListener('pointerdown', closeOnOutsidePointer)
    document.removeEventListener('keydown', closeOnEscape)
  })
})
</script>
