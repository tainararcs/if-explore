<!-- Formulário do pedido à IA: texto livre com contador e opção de considerar as preferências. -->
<template>
  <form
    class="flex flex-col gap-4 rounded-lg border border-border bg-surface p-4 sm:p-6"
    @submit.prevent="emit('submit')"
  >
    <div class="flex flex-col gap-2">
      <label
        :for="fieldId"
        class="font-semibold"
      >
        {{ t('discovery.label') }}
      </label>
      <textarea
        :id="fieldId"
        ref="field"
        v-model="query"
        class="min-h-28 w-full resize-y rounded-md border-[1.5px] border-border-strong bg-bg p-3 text-text [font:inherit] transition-[border-color] duration-(--duration-fast) ease-standard placeholder:text-text-muted hover:border-primary-hover focus-visible:border-primary focus-visible:outline-3 focus-visible:outline-offset-0 focus-visible:outline-primary/30"
        rows="3"
        :maxlength="MAX_QUERY_LENGTH"
        enterkeyhint="send"
        :placeholder="t('discovery.placeholder')"
        :aria-describedby="counterId"
        @keydown.enter="submitOnEnter"
      />
      <p
        :id="counterId"
        class="m-0 self-end text-caption text-text-muted"
      >
        {{ t('discovery.counter', { n: query.length, max: MAX_QUERY_LENGTH }) }}
      </p>
    </div>

    <label
      v-if="showPreferenceToggle"
      class="flex cursor-pointer items-center gap-3 text-small"
    >
      <input
        v-model="usePreferences"
        type="checkbox"
        class="size-5 shrink-0 accent-primary"
      >
      {{ t('discovery.usePreferences') }}
    </label>

    <button
      type="submit"
      class="button button--primary w-full"
      :disabled="!canSubmit"
    >
      <IconSparkle class="size-5" />
      {{ isLoading ? t('discovery.submitting') : t('discovery.submit') }}
    </button>
  </form>
</template>

<script setup lang="ts">
import { useId, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import IconSparkle from '../../../components/icons/IconSparkle.vue'
import { MAX_QUERY_LENGTH } from '../models/discovery'

interface Props {
  canSubmit: boolean
  isLoading: boolean
  /** Mostra a opção de considerar as preferências (só quando há preferências salvas). */
  showPreferenceToggle: boolean
}

defineProps<Props>()

const query = defineModel<string>('query', { required: true })
const usePreferences = defineModel<boolean>('usePreferences', { required: true })

const emit = defineEmits<{
  submit: []
}>()

const { t } = useI18n()

const fieldId = useId()
const counterId = useId()
const field = useTemplateRef<HTMLTextAreaElement>('field')

// Enter envia; Shift+Enter quebra a linha. Durante a composição (acentos, IME) o Enter é do teclado.
function submitOnEnter(event: KeyboardEvent): void {
  if (event.shiftKey || event.isComposing) {
    return
  }
  event.preventDefault()
  emit('submit')
}

defineExpose({
  /** Põe o foco no campo, com o cursor no fim do texto (ao editar um pedido). */
  focus(): void {
    const element = field.value
    element?.focus()
    element?.setSelectionRange(element.value.length, element.value.length)
  },
})
</script>
