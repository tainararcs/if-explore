<!-- Cabeçalho da aplicação com a marca e um espaço para ações contextuais da tela. -->
<template>
  <header
    class="border-b border-border bg-surface"
    :class="{ 'sticky top-0 z-10': sticky }"
  >
    <div class="container flex min-h-(--header-height) items-center justify-between gap-4">
      <RouterLink
        class="inline-flex min-h-11 items-center gap-3 text-text no-underline"
        :to="hasPreferences ? '/home' : '/'"
        :aria-label="t('common.brandHomeLabel')"
      >
        <BrandMark />
        <span class="font-display text-[1.25rem] leading-none">{{ t('common.appName') }}</span>
      </RouterLink>
      <div class="flex items-center gap-2">
        <slot name="actions" />
        <ThemeToggle />
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useReadingPreferences } from '../composables/useReadingPreferences'
import BrandMark from './BrandMark.vue'
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
const { hasPreferences } = useReadingPreferences()
</script>
