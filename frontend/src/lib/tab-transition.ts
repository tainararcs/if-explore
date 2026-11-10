import { nextTick } from 'vue'
import type { Router } from 'vue-router'

/** Direção em que a tela desliza ao trocar de aba no cabeçalho. */
type TabDirection = 'forward' | 'back'

// "Para você" (recomendações e o onboarding, que é o começo delas) fica à esquerda;
// "Pergunte à IA", à direita.
const TAB_PATHS: readonly (readonly string[])[] = [['/home', '/onboarding'], ['/discover']]

/**
 * Indica a qual aba do cabeçalho um caminho pertence.
 *
 * @param path Caminho da rota, sem query nem hash.
 * @returns Posição da aba (0 = "Para você", 1 = "Pergunte à IA") ou `null`
 * quando a tela não pertence a nenhuma aba.
 */
export function tabIndexOf(path: string): number | null {
  const index = TAB_PATHS.findIndex((paths) => paths.includes(path))
  return index === -1 ? null : index
}

function tabDirection(fromPath: string, toPath: string): TabDirection | null {
  const from = tabIndexOf(fromPath)
  const to = tabIndexOf(toPath)
  if (from === null || to === null || from === to) {
    return null
  }
  return to > from ? 'forward' : 'back'
}

/**
 * Anima a troca entre as abas do cabeçalho com a View Transitions API: a tela
 * desliza para o lado da aba escolhida e o destaque da aba acompanha. As demais
 * navegações continuam instantâneas, assim como nos navegadores sem a API.
 * A direção vai em `data-tab-direction` no `<html>`, lido pelo CSS em `index.css`.
 *
 * @param router Roteador da aplicação.
 */
export function installTabTransition(router: Router): void {
  if (typeof document.startViewTransition !== 'function') {
    return
  }

  // Resolve quando a navegação em andamento termina (com ou sem sucesso).
  let finishNavigation: (() => void) | null = null
  router.afterEach(() => {
    finishNavigation?.()
    finishNavigation = null
  })

  router.beforeResolve((to, from) => {
    const direction = tabDirection(from.path, to.path)
    if (!direction) {
      return true
    }

    const root = document.documentElement
    root.dataset.tabDirection = direction
    const navigationDone = new Promise<void>((resolve) => {
      finishNavigation = resolve
    })

    // A navegação só segue dentro do callback, depois de o navegador capturar a tela
    // antiga; o callback termina quando a tela nova já foi renderizada.
    return new Promise<boolean>((continueNavigation) => {
      const transition = document.startViewTransition(async () => {
        continueNavigation(true)
        await navigationDone
        await nextTick()
      })
      // O navegador cancela a animação quando a janela muda de tamanho no meio dela
      // (girar o celular, redimensionar): `ready` é rejeitada, mas a navegação segue
      // normalmente, então não há erro a tratar.
      transition.ready.catch(() => undefined)
      void transition.finished.finally(() => {
        delete root.dataset.tabDirection
      })
    })
  })
}
