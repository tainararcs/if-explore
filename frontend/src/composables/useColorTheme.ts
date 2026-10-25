import { computed, ref } from 'vue'

/** Tema de cores efetivamente aplicado à interface. */
export type ColorTheme = 'light' | 'dark'

// A mesma chave é lida pelo script inline do index.html para evitar o flash de tema.
const STORAGE_KEY = 'if-explore:theme'

function isColorTheme(value: unknown): value is ColorTheme {
  return value === 'light' || value === 'dark'
}

function readStoredTheme(): ColorTheme | null {
  try {
    const value = window.localStorage.getItem(STORAGE_KEY)
    return isColorTheme(value) ? value : null
  } catch {
    return null
  }
}

function writeStoredTheme(theme: ColorTheme): void {
  try {
    window.localStorage.setItem(STORAGE_KEY, theme)
  } catch {
    // Sem armazenamento, a escolha vale apenas até recarregar a página.
  }
}

const systemQuery = window.matchMedia('(prefers-color-scheme: dark)')

// Estado compartilhado: escolha manual do visitante e tema atual do sistema.
const chosenTheme = ref<ColorTheme | null>(readStoredTheme())
const systemTheme = ref<ColorTheme>(systemQuery.matches ? 'dark' : 'light')

// O ouvinte vive enquanto a aplicação estiver aberta, por isso não é removido.
systemQuery.addEventListener('change', (event) => {
  systemTheme.value = event.matches ? 'dark' : 'light'
})

/**
 * Controla o tema claro/escuro. Sem escolha manual, segue o sistema; a escolha
 * do visitante é salva no navegador e aplicada via atributo `data-theme`.
 *
 * @returns Tema efetivo e ação para alternar entre claro e escuro.
 */
export function useColorTheme() {
  const theme = computed<ColorTheme>(() => chosenTheme.value ?? systemTheme.value)

  function toggleTheme(): void {
    const next: ColorTheme = theme.value === 'dark' ? 'light' : 'dark'
    chosenTheme.value = next
    document.documentElement.dataset.theme = next
    writeStoredTheme(next)
  }

  return {
    theme,
    toggleTheme,
  }
}
