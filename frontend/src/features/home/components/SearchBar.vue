<!-- Campo de busca do acervo com ícone e botão para limpar. -->
<template>
  <div
    class="relative flex items-center"
    role="search"
  >
    <label
      :for="inputId"
      class="sr-only"
    >
      {{ t('home.search.label') }}
    </label>
    <IconSearch class="pointer-events-none absolute left-4 size-5 text-text-muted" />
    <input
      :id="inputId"
      v-model="model"
      class="min-h-13 w-full appearance-none rounded-pill border-[1.5px] border-border bg-surface py-0 pr-13 pl-12 text-text [font:inherit] transition-[border-color] duration-(--duration-fast) ease-standard placeholder:text-text-muted hover:border-primary-hover focus-visible:border-primary focus-visible:outline-offset-1 [&::-webkit-search-cancel-button]:hidden"
      type="search"
      enterkeyhint="search"
      autocomplete="off"
      :placeholder="t('home.search.placeholder')"
    >
    <button
      v-if="model"
      type="button"
      class="absolute right-1 grid size-11 cursor-pointer place-items-center rounded-[50%] border-0 bg-transparent p-0 text-text-muted hover:bg-surface-muted hover:text-text"
      :aria-label="t('home.search.clear')"
      @click="emit('clear')"
    >
      <IconClose class="size-5" />
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
