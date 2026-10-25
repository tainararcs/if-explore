<!-- Campo de busca do acervo com ícone e botão para limpar. -->
<template>
  <div
    class="search-bar"
    role="search"
  >
    <label
      :for="inputId"
      class="visually-hidden"
    >
      {{ t('home.search.label') }}
    </label>
    <IconSearch class="search-bar__icon" />
    <input
      :id="inputId"
      v-model="model"
      class="search-bar__input"
      type="search"
      enterkeyhint="search"
      autocomplete="off"
      :placeholder="t('home.search.placeholder')"
    >
    <button
      v-if="model"
      type="button"
      class="search-bar__clear"
      :aria-label="t('home.search.clear')"
      @click="emit('clear')"
    >
      <IconClose />
    </button>
  </div>
</template>

<script setup lang="ts">
import { useId } from 'vue'
import { useI18n } from 'vue-i18n'
import IconClose from '../../../components/icons/IconClose.vue'
import IconSearch from '../../../components/icons/IconSearch.vue'

const model = defineModel<string>({ required: true })

const emit = defineEmits<{
  clear: []
}>()

const { t } = useI18n()
const inputId = useId()
</script>

<style scoped>
.search-bar {
  position: relative;
  display: flex;
  align-items: center;
}

.search-bar__icon {
  position: absolute;
  left: var(--space-4);
  width: 20px;
  height: 20px;
  color: var(--color-text-muted);
  pointer-events: none;
}

.search-bar__input {
  width: 100%;
  min-height: 52px;
  padding: 0 52px 0 calc(var(--space-4) + 20px + var(--space-3));
  border: 1.5px solid var(--color-border);
  border-radius: var(--radius-pill);
  background: var(--color-surface);
  color: var(--color-text);
  font: inherit;
  appearance: none;
  transition: border-color var(--duration-fast) var(--ease-standard);
}

.search-bar__input::placeholder {
  color: var(--color-text-muted);
}

.search-bar__input:hover {
  border-color: var(--color-primary-hover);
}

.search-bar__input:focus-visible {
  border-color: var(--color-primary);
  outline-offset: 1px;
}

/* O botão próprio de limpar substitui o nativo, que varia entre navegadores. */
.search-bar__input::-webkit-search-cancel-button {
  display: none;
}

.search-bar__clear {
  position: absolute;
  right: var(--space-1);
  display: grid;
  place-items: center;
  width: 44px;
  height: 44px;
  padding: 0;
  border: 0;
  border-radius: 50%;
  background: transparent;
  color: var(--color-text-muted);
  cursor: pointer;
}

.search-bar__clear:hover {
  background: var(--color-surface-muted);
  color: var(--color-text);
}

.search-bar__clear :deep(svg) {
  width: 20px;
  height: 20px;
}
</style>
