import { createI18n } from 'vue-i18n'
import { ptBR, type MessageSchema } from '../locales/pt-BR'

/**
 * Instância do vue-i18n na Composition API. Apenas pt-BR é suportado.
 */
export const i18n = createI18n<[MessageSchema], 'pt-BR', false>({
  legacy: false,
  locale: 'pt-BR',
  fallbackLocale: 'pt-BR',
  messages: {
    'pt-BR': ptBR,
  },
})
