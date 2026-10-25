<!-- Cabeçalho da aplicação com a marca e um espaço para ações contextuais da tela. -->
<template>
  <header
    class="app-header"
    :class="{ 'app-header--sticky': sticky }"
  >
    <div class="app-header__inner container">
      <RouterLink
        class="app-header__brand"
        :to="hasPreferences ? '/home' : '/'"
        :aria-label="t('common.brandHomeLabel')"
      >
        <BrandMark />
        <span class="app-header__name">{{ t('common.appName') }}</span>
      </RouterLink>
      <div class="app-header__actions">
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

<style scoped>
.app-header {
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
}

.app-header--sticky {
  position: sticky;
  top: 0;
  z-index: 10;
}

.app-header__inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  min-height: var(--header-height);
}

.app-header__brand {
  display: inline-flex;
  align-items: center;
  gap: var(--space-3);
  min-height: 44px;
  color: var(--color-text);
  text-decoration: none;
}

.app-header__name {
  font-family: var(--font-display);
  font-size: 1.25rem;
  line-height: 1;
}

.app-header__actions {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}
</style>
