/**
 * Copia texto para a área de transferência.
 *
 * Usa a Clipboard API e, quando ela não existe (páginas sem HTTPS, como o
 * servidor de desenvolvimento acessado pelo IP da rede no celular) ou é
 * recusada, recorre a um campo temporário com `execCommand('copy')`.
 *
 * @param text - Texto a copiar.
 * @throws Error quando nenhum dos métodos consegue copiar.
 */
export async function copyText(text: string): Promise<void> {
  if (navigator.clipboard) {
    try {
      await navigator.clipboard.writeText(text)
      return
    } catch {
      // Segue para o método alternativo.
    }
  }
  if (!copyWithTemporaryField(text)) {
    throw new Error('Clipboard unavailable')
  }
}

// Método legado, ainda suportado pelos navegadores, para contextos sem Clipboard API.
function copyWithTemporaryField(text: string): boolean {
  const field = document.createElement('textarea')
  field.value = text
  field.setAttribute('readonly', '')
  field.style.position = 'fixed'
  field.style.opacity = '0'
  document.body.append(field)
  const previousFocus = document.activeElement
  field.select()
  try {
    return document.execCommand('copy')
  } catch {
    return false
  } finally {
    field.remove()
    if (previousFocus instanceof HTMLElement) {
      previousFocus.focus()
    }
  }
}
