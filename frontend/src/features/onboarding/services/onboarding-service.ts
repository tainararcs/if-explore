import { http } from '../../../lib/http-client'
import type { Book } from '../../../models/book'
import { list, parseBook } from '../../../services/catalog-parsers'

/** Quantos títulos o visitante vê para escolher em cada recorte. */
export const CANDIDATE_LIMIT = 12

/** Escolhas do primeiro passo que definem os candidatos. */
export interface CandidateInterests {
  genreIds: readonly string[]
  areaIds: readonly string[]
  courseIds: readonly string[]
}

/**
 * Títulos para o visitante escolher: os gêneros escolhidos, as áreas escolhidas
 * e as dos cursos marcados se intercalam na lista, gêneros primeiro; dentro de
 * cada área, os livros dos cursos marcados vêm primeiro. A API completa com
 * outros títulos quando sobram poucos.
 *
 * @param interests - Gêneros, áreas e cursos escolhidos.
 * @param signal - Cancela a requisição quando as escolhas mudam de novo.
 * @returns Candidatos já ordenados.
 */
export async function getOnboardingCandidates(
  interests: CandidateInterests,
  signal?: AbortSignal,
): Promise<Book[]> {
  const { data } = await http.get<unknown>('/recommendations/candidates', {
    params: {
      genre: interests.genreIds,
      area: interests.areaIds,
      course: interests.courseIds,
      limit: CANDIDATE_LIMIT,
    },
    signal,
  })
  return list(data, 'candidates', parseBook)
}
