import { computed, readonly, ref } from 'vue'
import {
  isCompletePreferences,
  type ReadingPreferences,
} from '../models/reading-preferences'
import {
  clearPreferences,
  loadPreferences,
  savePreferences,
} from '../services/preferences-storage'

// Estado compartilhado entre todas as telas; a memória continua válida mesmo
// quando o armazenamento do navegador falha.
const preferences = ref<ReadingPreferences | null>(loadPreferences())

/**
 * Expõe as preferências de leitura do visitante de forma reativa.
 *
 * @returns Preferências atuais, indicador de preferências completas e ações
 * para salvar ou limpar.
 */
export function useReadingPreferences() {
  const hasPreferences = computed(() => isCompletePreferences(preferences.value))

  /**
   * Atualiza as preferências em memória e tenta persisti-las.
   *
   * @returns `true` quando também foram gravadas no navegador.
   */
  function save(next: Omit<ReadingPreferences, 'version' | 'updatedAt'>): boolean {
    const value: ReadingPreferences = {
      ...next,
      version: 1,
      updatedAt: new Date().toISOString(),
    }
    preferences.value = value
    return savePreferences(value)
  }

  function clear(): void {
    preferences.value = null
    clearPreferences()
  }

  return {
    preferences: readonly(preferences),
    hasPreferences,
    save,
    clear,
  }
}
