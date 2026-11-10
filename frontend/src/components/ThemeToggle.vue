<!--
  Item "Tema escuro" do menu do cabeçalho: uma chave liga/desliga com rótulo,
  que alterna entre os temas claro e escuro.
-->
<template>
  <button
    type="button"
    role="switch"
    class="flex min-h-11 w-full cursor-pointer items-center gap-3 rounded-sm border-0 bg-transparent px-3 text-start font-body text-small font-semibold text-text hover:bg-surface-muted"
    :aria-checked="isDark"
    @click="toggleTheme"
  >
    <IconMoon class="size-5 shrink-0 text-primary" />
    <span class="flex-1">{{ t('common.theme.dark') }}</span>
    <!-- Trilho e botão da chave; o estado também é anunciado por aria-checked. -->
    <span
      class="relative h-6 w-10 shrink-0 rounded-pill border border-border transition-colors duration-(--duration-base) ease-standard"
      :class="isDark ? 'border-primary bg-primary' : 'bg-surface-muted'"
      aria-hidden="true"
    >
      <span
        class="absolute top-0.5 left-0.5 size-[18px] rounded-pill bg-surface shadow-sm motion-safe:transition-transform motion-safe:duration-(--duration-base) motion-safe:ease-standard"
        :class="{ 'translate-x-4': isDark }"
      />
    </span>
  </button>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useColorTheme } from '../composables/useColorTheme'
import IconMoon from './icons/IconMoon.vue'

const { t } = useI18n()
const { theme, toggleTheme } = useColorTheme()

const isDark = computed(() => theme.value === 'dark')
</script>
