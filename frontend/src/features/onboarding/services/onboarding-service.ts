import { http } from '../../../lib/http-client'
import type { Book } from '../../../models/book'
import { list, parseBook } from '../../../services/catalog-parsers'

/** Quantos títulos o visitante vê para escolher. */
const CANDIDATE_LIMIT = 60

/**
 * Títulos para o visitante escolher: as áreas escolhidas (e as dos cursos
 * marcados) se intercalam na lista e, dentro de cada área, os livros dos cursos
 * marcados vêm primeiro; a API completa com outros títulos quando sobram poucos.
 *
 * @param areaIds - Áreas escolhidas.
 * @param courseIds - Cursos escolhidos.
 * @param signal - Cancela a requisição quando as escolhas mudam de novo.
 * @returns Candidatos já ordenados.
 */
export async function getOnboardingCandidates(
  areaIds: readonly string[],
  courseIds: readonly string[],
  signal?: AbortSignal,
): Promise<Book[]> {
  const { data } = await http.get<unknown>('/recommendations/candidates', {
    params: { area: areaIds, course: courseIds, limit: CANDIDATE_LIMIT },
    signal,
  })
  return list(data, 'candidates', parseBook)
}
