import { HttpClient } from '../../../lib/http/HttpClient'
import type { Book } from '../../../models/book'
import { list, parseBook } from '../../../services/catalog-parsers'

const http = new HttpClient().instance

/** Quantos títulos o visitante vê para escolher. */
export const CANDIDATE_LIMIT = 60

/**
 * Títulos para o visitante escolher: primeiro os dos cursos marcados, depois os
 * das áreas; a API completa com outros títulos quando sobram poucos.
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
