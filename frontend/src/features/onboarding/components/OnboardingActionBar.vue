<!-- Barra de ações fixa no rodapé do onboarding, com dica/contador e botões do passo. -->
<template>
  <div class="sticky bottom-0 z-5 border-t border-border bg-surface pt-3 pb-[calc(var(--space-3)+env(safe-area-inset-bottom))] shadow-[0_-6px_20px_light-dark(rgb(36_39_34/0.06),rgb(0_0_0/0.3))]">
    <div class="container flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
      <div
        class="text-small text-text-muted empty:hidden"
        aria-live="polite"
      >
        <slot name="hint" />
      </div>
      <div class="flex flex-col-reverse gap-2 sm:flex-row">
        <slot />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineSlots<{
  hint?: () => unknown
  default: () => unknown
}>()
</script>
