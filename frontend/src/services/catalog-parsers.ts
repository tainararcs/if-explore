import { COPY_STATUSES, type Book, type BookCopies, type BookDetail, type BookLink, type CopyStatus } from '../models/book'
import { COURSE_LEVELS, type Course, type CourseLevel, type KnowledgeArea, type LiteraryGenre } from '../models/taxonomy'

/** Resposta da API fora do contrato esperado. */
export class ApiContractError extends Error {
  constructor(path: string) {
    super(`Resposta inesperada da API em ${path}`)
    this.name = 'ApiContractError'
  }
}

type JsonRecord = Record<string, unknown>

function isRecord(value: unknown): value is JsonRecord {
  return typeof value === 'object' && value !== null && !Array.isArray(value)
}

function record(value: unknown, path: string): JsonRecord {
  if (!isRecord(value)) {
    throw new ApiContractError(path)
  }
  return value
}

function string(value: unknown, path: string): string {
  if (typeof value !== 'string') {
    throw new ApiContractError(path)
  }
  return value
}

function nullableString(value: unknown, path: string): string | null {
  return value === null ? null : string(value, path)
}

function number(value: unknown, path: string): number {
  if (typeof value !== 'number' || !Number.isFinite(value)) {
    throw new ApiContractError(path)
  }
  return value
}

function nullableNumber(value: unknown, path: string): number | null {
  return value === null ? null : number(value, path)
}

function stringList(value: unknown, path: string): string[] {
  return list(value, path, (item, itemPath) => string(item, itemPath))
}

/**
 * Valida uma lista da resposta, item a item.
 *
 * @param value - Valor recebido.
 * @param path - Caminho do valor na resposta, usado na mensagem de erro.
 * @param parseItem - Validação de cada item.
 * @returns Os itens validados.
 * @throws ApiContractError quando o valor não é uma lista ou um item é inválido.
 */
export function list<T>(value: unknown, path: string, parseItem: (item: unknown, path: string) => T): T[] {
  if (!Array.isArray(value)) {
    throw new ApiContractError(path)
  }
  return value.map((item: unknown, index) => parseItem(item, `${path}[${index}]`))
}

function isCourseLevel(value: string): value is CourseLevel {
  return COURSE_LEVELS.some((level) => level === value)
}

export function parseArea(value: unknown, path = 'area'): KnowledgeArea {
  const data = record(value, path)
  return { id: string(data.id, `${path}.id`), name: string(data.name, `${path}.name`) }
}

export function parseGenre(value: unknown, path = 'genre'): LiteraryGenre {
  const data = record(value, path)
  return { id: string(data.id, `${path}.id`), name: string(data.name, `${path}.name`) }
}

export function parseCourse(value: unknown, path = 'course'): Course {
  const data = record(value, path)
  const level = string(data.level, `${path}.level`)
  if (!isCourseLevel(level)) {
    throw new ApiContractError(`${path}.level`)
  }
  return {
    id: string(data.id, `${path}.id`),
    name: string(data.name, `${path}.name`),
    areaId: string(data.areaId, `${path}.areaId`),
    level,
  }
}

function isCopyStatus(value: unknown): value is CopyStatus {
  return COPY_STATUSES.some((status) => status === value)
}

function parseCopies(value: unknown, path: string): BookCopies | null {
  if (value === null) {
    return null
  }
  const data = record(value, path)
  if (!isCopyStatus(data.status)) {
    throw new ApiContractError(`${path}.status`)
  }
  return {
    total: number(data.total, `${path}.total`),
    status: data.status,
    available: nullableNumber(data.available, `${path}.available`),
    updatedAt: string(data.updatedAt, `${path}.updatedAt`),
  }
}

/**
 * Valida um livro da API (formato de listas e prateleiras).
 *
 * @throws ApiContractError quando algum campo está fora do contrato.
 */
export function parseBook(value: unknown, path = 'book'): Book {
  const data = record(value, path)
  const field = (name: string) => `${path}.${name}`
  return {
    id: string(data.id, field('id')),
    title: string(data.title, field('title')),
    subtitle: nullableString(data.subtitle, field('subtitle')),
    authors: stringList(data.authors, field('authors')),
    year: nullableNumber(data.year, field('year')),
    areaId: nullableString(data.areaId, field('areaId')),
    courseIds: stringList(data.courseIds, field('courseIds')),
    genreIds: stringList(data.genreIds, field('genreIds')),
    subjects: stringList(data.subjects, field('subjects')),
    synopsis: nullableString(data.synopsis, field('synopsis')),
    callNumber: nullableString(data.callNumber, field('callNumber')),
    isbn: nullableString(data.isbn, field('isbn')),
    publisher: nullableString(data.publisher, field('publisher')),
    edition: nullableString(data.edition, field('edition')),
    pages: nullableNumber(data.pages, field('pages')),
    documentType: nullableString(data.documentType, field('documentType')),
    coverUrl: nullableString(data.coverUrl, field('coverUrl')),
    copies: parseCopies(data.copies, field('copies')),
  }
}

function parseLink(value: unknown, path: string): BookLink {
  const data = record(value, path)
  return { label: string(data.label, `${path}.label`), url: string(data.url, `${path}.url`) }
}

/**
 * Valida o livro completo da página do título.
 *
 * @throws ApiContractError quando algum campo está fora do contrato.
 */
export function parseBookDetail(value: unknown, path = 'book'): BookDetail {
  const data = record(value, path)
  const field = (name: string) => `${path}.${name}`
  return {
    ...parseBook(data, path),
    contributors: nullableString(data.contributors, field('contributors')),
    city: nullableString(data.city, field('city')),
    country: nullableString(data.country, field('country')),
    volume: nullableString(data.volume, field('volume')),
    series: nullableString(data.series, field('series')),
    physicalDescription: nullableString(data.physicalDescription, field('physicalDescription')),
    issn: nullableString(data.issn, field('issn')),
    issue: nullableString(data.issue, field('issue')),
    languages: stringList(data.languages, field('languages')),
    notes: stringList(data.notes, field('notes')),
    links: list(data.links, field('links'), parseLink),
    tccCourse: nullableString(data.tccCourse, field('tccCourse')),
    catalogedAt: nullableString(data.catalogedAt, field('catalogedAt')),
    loans: nullableNumber(data.loans, field('loans')),
  }
}

/** Página de resultados da busca. */
export interface BookPage {
  items: Book[]
  total: number
  page: number
  pageSize: number
}

export function parseBookPage(value: unknown, path = 'page'): BookPage {
  const data = record(value, path)
  return {
    items: list(data.items, `${path}.items`, parseBook),
    total: number(data.total, `${path}.total`),
    page: number(data.page, `${path}.page`),
    pageSize: number(data.pageSize, `${path}.pageSize`),
  }
}

export { nullableString as parseNullableString, record as parseRecord, string as parseString }
