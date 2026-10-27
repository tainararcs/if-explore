<!-- Botão que alterna entre os temas claro e escuro, com troca animada de ícone. -->
<template>
  <button
    type="button"
    class="relative grid size-11 cursor-pointer place-items-center rounded-[50%] border-0 bg-transparent p-0 text-text hover:bg-surface-muted"
    :aria-label="isDark ? t('common.theme.useLight') : t('common.theme.useDark')"
    :title="isDark ? t('common.theme.useLight') : t('common.theme.useDark')"
    @click="toggleTheme"
  >
    <!-- No tema claro mostra a lua (ação: escurecer); no escuro, o sol. -->
    <IconSun :class="[iconClass, { [hiddenIconClass]: !isDark }]" />
    <IconMoon :class="[iconClass, { [hiddenIconClass]: isDark }]" />
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

// Os dois ícones ocupam a mesma célula. O esmaecimento vale sempre; o giro só
// quando o sistema permite movimento.
const iconClass =
  'col-start-1 row-start-1 transition-opacity duration-(--duration-base) ease-standard motion-safe:transition-[opacity,rotate,scale]'
const hiddenIconClass = '-rotate-90 scale-50 opacity-0'
</script>
