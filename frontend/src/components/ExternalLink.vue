<!-- Link para outro site: abre em nova aba, com ícone e aviso para leitores de tela. -->
<template>
  <a
    :href="href"
    target="_blank"
    rel="noopener noreferrer"
    class="inline-flex items-center gap-1"
  >
    <slot />
    <IconExternalLink class="size-3.5 shrink-0" />
    <span class="sr-only">{{ t('common.opensInNewTab') }}</span>
  </a>
</template>

<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import IconExternalLink from './icons/IconExternalLink.vue'

interface Props {
  href: string
}

defineProps<Props>()

const { t } = useI18n()
</script>
