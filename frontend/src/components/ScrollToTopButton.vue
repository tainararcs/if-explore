<!-- Botão flutuante que retorna ao início após a pessoa rolar a página. -->
<template>
  <button
    v-if="isVisible"
    type="button"
    class="fixed end-4 z-30 grid size-12 cursor-pointer place-items-center rounded-[50%] border-0 bg-primary p-0 text-on-primary shadow-md hover:bg-primary-hover sm:end-6"
    :aria-label="t('common.scrollToTop')"
    :style="{ bottom: `${bottomOffset}px` }"
    @click="scrollToTop"
  >
    <svg
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      stroke-width="1.5"
      stroke-linecap="round"
      stroke-linejoin="round"
      aria-hidden="true"
      focusable="false"
    >
      <path d="M12 19V5M6 11l6-6 6 6" />
    </svg>
  </button>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'

const SCROLL_THRESHOLD = 400
const BOTTOM_GAP = 16
const BUTTON_SIZE = 48

const { t } = useI18n()
const isVisible = ref(false)
const bottomOffset = ref(BOTTOM_GAP)
let overlayObserver: MutationObserver | undefined

function updateButtonPosition(): void {
  isVisible.value = window.scrollY > SCROLL_THRESHOLD

  const overlays = document.querySelectorAll<HTMLElement>('[data-bottom-overlay]')
  const viewportBottom = window.innerHeight
  const buttonTop = viewportBottom - BOTTOM_GAP - BUTTON_SIZE
  const buttonBottom = viewportBottom - BOTTOM_GAP
  const overlay = Array.from(overlays)
    .map((element) => element.getBoundingClientRect())
    .find((bounds) => bounds.top < buttonBottom && bounds.bottom > buttonTop)

  bottomOffset.value = overlay
    ? viewportBottom - overlay.top + BOTTOM_GAP
    : BOTTOM_GAP
}

function scrollToTop(): void {
  const behavior = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    ? 'auto'
    : 'smooth'

  window.scrollTo({ top: 0, behavior })
}

onMounted(() => {
  updateButtonPosition()
  window.addEventListener('scroll', updateButtonPosition, { passive: true })
  window.addEventListener('resize', updateButtonPosition)
  overlayObserver = new MutationObserver(updateButtonPosition)
  overlayObserver.observe(document.body, { childList: true, subtree: true })
})

onUnmounted(() => {
  window.removeEventListener('scroll', updateButtonPosition)
  window.removeEventListener('resize', updateButtonPosition)
  overlayObserver?.disconnect()
})
</script>
