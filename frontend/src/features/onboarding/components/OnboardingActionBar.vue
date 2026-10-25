<!-- Barra de ações fixa no rodapé do onboarding, com dica/contador e botões do passo. -->
<template>
  <div class="action-bar">
    <div class="action-bar__inner container">
      <div
        class="action-bar__hint"
        aria-live="polite"
      >
        <slot name="hint" />
      </div>
      <div class="action-bar__actions">
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

<style scoped>
.action-bar {
  position: sticky;
  bottom: 0;
  z-index: 5;
  padding-block: var(--space-3) calc(var(--space-3) + env(safe-area-inset-bottom));
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
  box-shadow: 0 -6px 20px light-dark(rgb(36 39 34 / 0.06), rgb(0 0 0 / 0.3));
}

.action-bar__inner {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.action-bar__hint {
  font-size: var(--text-small);
  color: var(--color-text-muted);
}

.action-bar__hint:empty {
  display: none;
}

.action-bar__actions {
  display: flex;
  flex-direction: column-reverse;
  gap: var(--space-2);
}

@media (min-width: 600px) {
  .action-bar__inner {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }

  .action-bar__actions {
    flex-direction: row;
  }
}
</style>
