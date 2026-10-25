import type { Book } from '../../../models/book'
import type { KnowledgeArea, LiteraryGenre } from '../../../models/taxonomy'
import {
  getBooks,
  getKnowledgeAreas,
  getLiteraryGenres,
} from '../../../services/catalog-service'
import type {
  HomeRecommendations,
  RecommendationProfile,
  Shelf,
} from '../models/recommendation'

const SHELF_SIZE = 12
const MIN_SHELF_SIZE = 3
const MAX_SEED_SHELVES = 3

function countShared(a: readonly string[], b: readonly string[]): number {
  return a.filter((item) => b.includes(item)).length
}

/**
 * Pontua a afinidade de um livro com o perfil do visitante.
 *
 * Peso: curso > área > gênero > assuntos em comum com os títulos escolhidos.
 *
 * @param book - Livro avaliado.
 * @param profile - Preferências do visitante.
 * @param seedSubjects - Assuntos dos títulos escolhidos no onboarding.
 * @returns Pontuação; zero indica nenhuma afinidade.
 */
export function scoreBook(
  book: Book,
  profile: RecommendationProfile,
  seedSubjects: readonly string[],
): number {
  let score = 0
  if (book.courseIds.some((id) => profile.courseIds.includes(id))) {
    score += 4
  }
  if (profile.areaIds.includes(book.areaId)) {
    score += 2
  }
  if (book.genreIds.some((id) => profile.genreIds.includes(id))) {
    score += 1.5
  }
  return score + countShared(book.subjects, seedSubjects)
}

/**
 * Monta as prateleiras da home a partir do acervo e do perfil. Função pura,
 * independente da fonte dos dados.
 *
 * @returns Prateleiras com pelo menos três livros, sem repetir os títulos
 * escolhidos pelo visitante.
 */
export function buildShelves(
  books: readonly Book[],
  areas: readonly KnowledgeArea[],
  genres: readonly LiteraryGenre[],
  profile: RecommendationProfile,
): Shelf[] {
  const seeds = books.filter((book) => profile.seedBookIds.includes(book.id))
  const seedSubjects = seeds.flatMap((book) => book.subjects)
  const pool = books.filter((book) => !profile.seedBookIds.includes(book.id))

  const byScore = (list: Book[]) =>
    list
      .map((book) => ({ book, score: scoreBook(book, profile, seedSubjects) }))
      .sort((a, b) => b.score - a.score)
      .map((entry) => entry.book)

  const shelves: Shelf[] = [
    {
      id: 'for-you',
      kind: 'forYou',
      books: byScore(pool.filter((book) => scoreBook(book, profile, seedSubjects) > 0)).slice(
        0,
        SHELF_SIZE,
      ),
    },
  ]

  for (const seed of seeds.slice(0, MAX_SEED_SHELVES)) {
    const related = pool
      .map((book) => ({
        book,
        affinity:
          countShared(book.subjects, seed.subjects) * 2 +
          countShared(book.authors, seed.authors) * 3 +
          (book.areaId === seed.areaId ? 1 : 0),
      }))
      .filter((entry) => entry.affinity > 1)
      .sort((a, b) => b.affinity - a.affinity)
      .map((entry) => entry.book)
    shelves.push({
      id: `because-${seed.id}`,
      kind: 'becauseYouChose',
      subject: seed.title,
      books: related.slice(0, SHELF_SIZE),
    })
  }

  for (const area of areas.filter((item) => profile.areaIds.includes(item.id))) {
    shelves.push({
      id: `area-${area.id}`,
      kind: 'moreFromArea',
      subject: area.name,
      books: byScore(pool.filter((book) => book.areaId === area.id)).slice(0, SHELF_SIZE),
    })
  }

  for (const genre of genres.filter((item) => profile.genreIds.includes(item.id))) {
    shelves.push({
      id: `genre-${genre.id}`,
      kind: 'forPleasure',
      subject: genre.name,
      books: pool.filter((book) => book.genreIds.includes(genre.id)).slice(0, SHELF_SIZE),
    })
  }

  return shelves.filter((shelf) => shelf.books.length >= MIN_SHELF_SIZE)
}

/**
 * Obtém as recomendações da home. Simula o futuro serviço de recomendação
 * com IA usando apenas o acervo fictício local.
 *
 * @param profile - Preferências salvas do visitante.
 * @returns Prateleiras e áreas escolhidas.
 */
export async function getHomeRecommendations(
  profile: RecommendationProfile,
): Promise<HomeRecommendations> {
  const [books, areas, genres] = await Promise.all([
    getBooks(),
    getKnowledgeAreas(),
    getLiteraryGenres(),
  ])
  return {
    shelves: buildShelves(books, areas, genres, profile),
    areas: areas.filter((area) => profile.areaIds.includes(area.id)),
  }
}
