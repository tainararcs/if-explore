import { onUnmounted, ref, watch, type Ref } from 'vue'

/**
 * Indica se o elemento já saiu da tela pelo topo, ou seja, se o visitante
 * rolou além dele. Observa o elemento sempre que ele (re)aparece no DOM.
 *
 * @param target - Elemento observado (ref de template).
 * @returns `true` enquanto o elemento estiver acima da área visível.
 */
export function useScrolledPast(target: Ref<HTMLElement | null>) {
  const isPast = ref(false)

  const observer = new IntersectionObserver(([entry]) => {
    if (entry) {
      isPast.value = !entry.isIntersecting && entry.boundingClientRect.top < 0
    }
  })

  watch(
    target,
    (element, previous) => {
      if (previous) {
        observer.unobserve(previous)
      }
      if (element) {
        observer.observe(element)
      } else {
        isPast.value = false
      }
    },
    { immediate: true },
  )

  onUnmounted(() => observer.disconnect())

  return isPast
}
