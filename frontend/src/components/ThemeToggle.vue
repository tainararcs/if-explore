<!-- Botão que alterna entre os temas claro e escuro, com troca animada de ícone. -->
<template>
  <button
    type="button"
    class="theme-toggle"
    :class="`theme-toggle--${theme}`"
    :aria-label="isDark ? t('common.theme.useLight') : t('common.theme.useDark')"
    :title="isDark ? t('common.theme.useLight') : t('common.theme.useDark')"
    @click="toggleTheme"
  >
    <IconSun class="theme-toggle__icon theme-toggle__icon--sun" />
    <IconMoon class="theme-toggle__icon theme-toggle__icon--moon" />
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useColorTheme } from '../composables/useColorTheme'
import IconMoon from './icons/IconMoon.vue'
import IconSun from './icons/IconSun.vue'

const { t } = useI18n()
const { theme, toggleTheme } = useColorTheme()

const isDark = computed(() => theme.value === 'dark')
</script>

<style scoped>
.theme-toggle {
  position: relative;
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  padding: 0;
  border: 0;
  border-radius: 50%;
  background: transparent;
  color: var(--color-text);
  cursor: pointer;
}

.theme-toggle:hover {
  background: var(--color-surface-muted);
}

/* Os dois ícones ocupam a mesma célula; o inativo fica girado e reduzido.
   O esmaecimento vale sempre; o giro só quando o sistema permite movimento. */
.theme-toggle__icon {
  grid-area: 1 / 1;
  transition: opacity var(--duration-base) var(--ease-standard);
}

/* No tema claro mostra a lua (ação: escurecer); no escuro, o sol. */
.theme-toggle--light .theme-toggle__icon--sun,
.theme-toggle--dark .theme-toggle__icon--moon {
  opacity: 0;
  transform: rotate(-90deg) scale(0.5);
}

@media (prefers-reduced-motion: no-preference) {
  .theme-toggle__icon {
    transition:
      opacity var(--duration-base) var(--ease-standard),
      transform var(--duration-base) var(--ease-standard);
  }
}
</style>
