// Formatação dos textos do catálogo da biblioteca para exibição. O catálogo grava
// nomes como "SOBRENOME, Nome" e assuntos em maiúsculas; os dados originais
// continuam sendo usados para filtros e comparações.

const LOCALE = 'pt-BR'
// Partículas que ficam em minúsculas no meio de sobrenomes ("Cruz e Sousa").
const NAME_PARTICLES = new Set(['da', 'das', 'de', 'do', 'dos', 'e', 'y', 'van', 'von', 'del', 'la'])
const ET_AL = /\s+et\s+al\.?$/i
// Papel no fim do nome: "(orgs.)", "(ed.)", "(coord.)".
const ROLE = /\s*\((?:orgs?|eds?|coords?|comps?)\.?\)\.?$/i
const HAS_LOWERCASE = /\p{Ll}/u

function capitalize(word: string): string {
  return word.charAt(0).toLocaleUpperCase(LOCALE) + word.slice(1)
}

// "AB'SÁBER" -> "Ab'Sáber"; "ABOU-ID" -> "Abou-Id".
function titleCaseWord(word: string, isFirst: boolean): string {
  const lower = word.toLocaleLowerCase(LOCALE)
  if (!isFirst && NAME_PARTICLES.has(lower)) {
    return lower
  }
  return lower.replace(/(^|[-'’])(\p{L})/gu, (_, separator: string, letter: string) =>
    separator + letter.toLocaleUpperCase(LOCALE),
  )
}

function titleCase(text: string): string {
  return text
    .split(/\s+/)
    .filter(Boolean)
    .map((word, index) => titleCaseWord(word, index === 0))
    .join(' ')
}

/**
 * Converte um nome do catálogo ("SUMMERFIELD, Mark") para a ordem de leitura
 * ("Mark Summerfield").
 *
 * Vários nomes no mesmo campo, separados por ";", são formatados um a um. Nomes
 * sem vírgula (instituições, "ADONIAS FILHO") e com várias vírgulas ficam como
 * estão, para não embaralhar o que não segue o padrão.
 *
 * @param name - Nome como o catálogo grava.
 * @returns O nome para exibir.
 */
export function formatAuthorName(name: string): string {
  if (name.includes(';')) {
    return name.split(';').map((part) => formatAuthorName(part)).filter(Boolean).join(', ')
  }
  const role = ROLE.exec(name.trim())?.[0].trim()
  const trimmed = name.trim().replace(ROLE, '')
  if (role) {
    return `${formatAuthorName(trimmed)} ${role}`
  }
  const parts = trimmed.split(',')
  if (parts.length !== 2) {
    return trimmed
  }
  const [rawSurname = '', rawGiven = ''] = parts
  const surname = rawSurname.trim()
  let given = rawGiven.trim()
  const etAl = ET_AL.test(given)
  given = given.replace(ET_AL, '').trim()
  if (!surname || !given) {
    return trimmed
  }
  const displaySurname = HAS_LOWERCASE.test(surname) ? surname : titleCase(surname)
  return `${given} ${displaySurname}${etAl ? ' et al.' : ''}`
}

/**
 * Formata a lista de autores para exibir numa linha.
 *
 * @param authors - Nomes como o catálogo grava.
 * @returns Os nomes em ordem de leitura, separados por vírgula.
 */
export function formatAuthors(authors: readonly string[]): string {
  return authors.map(formatAuthorName).join(', ')
}

// Siglas sem vogal ("SQL", "HTML", "TCC") e termos com dígitos ou símbolos ("C++",
// "PNLD 2018/2020") ficam em maiúsculas.
function keepsUppercase(word: string): boolean {
  return /[\d+#/]/.test(word) || !/[AEIOUÁÉÍÓÚÂÊÔÃÕÀÜ]/i.test(word)
}

/**
 * Converte um assunto em maiúsculas ("LINGUAGEM DE PROGRAMAÇÃO") para a forma de
 * frase ("Linguagem de programação"). Assuntos já com minúsculas ficam como estão.
 *
 * @param subject - Assunto como o catálogo grava.
 * @returns O assunto para exibir.
 */
export function formatSubject(subject: string): string {
  const trimmed = subject.trim()
  if (HAS_LOWERCASE.test(trimmed)) {
    return trimmed
  }
  const sentence = trimmed
    .split(/(\s+)/)
    .map((word) => (keepsUppercase(word) ? word : word.toLocaleLowerCase(LOCALE)))
    .join('')
  return capitalize(sentence)
}
