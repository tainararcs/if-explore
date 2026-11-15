<!-- Página de erro: código, aviso curto e um botão para voltar. -->
<template>
  <div>
    <AppHeader />

    <main class="container flex min-h-[60dvh] max-w-[720px] flex-col items-start justify-center py-16">
      <p class="eyebrow">
        {{ t('errors.code', { code }) }}
      </p>
      <h1 class="mt-2">
        {{ t(`errors.${kind}.title`) }}
      </h1>
      <p class="mt-4 max-w-[65ch] text-text-muted">
        {{ t(`errors.${kind}.text`) }}
      </p>
      <button
        type="button"
        class="button button--primary mt-8"
        @click="goBack"
      >
        <IconArrowLeft class="size-5" />
        {{ t('errors.back') }}
      </button>
    </main>
  </div>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import AppHeader from '../../../components/AppHeader.vue'
import IconArrowLeft from '../../../components/icons/IconArrowLeft.vue'

interface Props {
  /** Código HTTP exibido acima do título. */
  code: 403 | 404 | 500
  /** Chave dos textos em `errors.*`. */
  kind: 'forbidden' | 'notFound' | 'serverError'
}

defineProps<Props>()

const { t } = useI18n()
const router = useRouter()

// Volta pelo histórico quando o visitante veio de outra tela da aplicação;
// quem abriu o endereço direto vai para as boas-vindas.
function goBack(): void {
  if (typeof router.options.history.state.back === 'string') {
    router.back()
    return
  }
  void router.push('/')
}
</script>
