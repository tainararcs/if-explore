import { isCancel } from 'axios'
import { computed, onUnmounted, ref, watch } from 'vue'
import { useReadingPreferences } from '../../../composables/useReadingPreferences'
import type { Book } from '../../../models/book'
import { REQUIRED_SEED_BOOKS } from '../../../models/reading-preferences'
import {
  COURSE_LEVELS,
  type Course,
  type KnowledgeArea,
  type LiteraryGenre,
} from '../../../models/taxonomy'
import {
  getBooksByIds,
  getCourses,
  getKnowledgeAreas,
  getLiteraryGenres,
} from '../../../services/catalog-service'
import {
  ALL_CANDIDATES,
  canFinish,
  filterKey,
  inferGenreIds,
  toggleValue,
  type CandidateFilter,
  type OnboardingDraft,
} from '../models/onboarding-draft'
import {
  CANDIDATE_LIMIT,
  getOnboardingCandidates,
  type CandidateInterests,
} from '../services/onboarding-service'

type LoadStatus = 'loading' | 'ready' | 'error'

/**
 * Concentra o estado do onboarding em uma tela: opções do acervo, mural de
 * títulos por recorte (todos os gêneros, um gênero ou uma área), escolhas e a
 * gravação final das preferências.
 *
 * Cada recorte é buscado uma vez e guardado; mudar áreas ou cursos descarta a
 * mistura "Todos", que os inclui. Títulos já escolhidos continuam à vista,
 * mesmo fora do recorte atual.
 *
 * O rascunho só vira preferência salva em `finish()`, que deduz os gêneros dos
 * títulos escolhidos; sair no meio do fluxo não altera as preferências existentes.
 */
export function useTasteOnboarding() {
  const { preferences, save } = useReadingPreferences()

  const status = ref<LoadStatus>('loading')
  const areas = ref<KnowledgeArea[]>([])
  const courses = ref<Course[]>([])
  const genres = ref<LiteraryGenre[]>([])
  // Livros já escolhidos, para que continuem visíveis fora do recorte atual.
  const selectedBooks = ref<Book[]>([])

  const draft = ref<OnboardingDraft>({ areaIds: [], courseIds: [], seedBookIds: [] })

  const activeFilter = ref<CandidateFilter>(ALL_CANDIDATES)
  const candidatesByFilter = ref(new Map<string, Book[]>())
  const candidatesStatus = ref<LoadStatus>('loading')

  const isComplete = computed(() => canFinish(draft.value))
  const missingBooks = computed(() => REQUIRED_SEED_BOOKS - draft.value.seedBookIds.length)

  const selectedAreas = computed(() =>
    areas.value.filter((area) => draft.value.areaIds.includes(area.id)),
  )
  const selectedCourses = computed(() =>
    courses.value.filter((course) => draft.value.courseIds.includes(course.id)),
  )

  /** Todos os cursos do campus agrupados por nível de ensino, sem níveis vazios. */
  const coursesByLevel = computed(() =>
    COURSE_LEVELS.map((level) => ({
      level,
      courses: courses.value.filter((course) => course.level === level),
    })).filter((group) => group.courses.length > 0),
  )

  const candidates = computed(
    () => candidatesByFilter.value.get(filterKey(activeFilter.value)) ?? [],
  )

  /**
   * Títulos do mural, no máximo `CANDIDATE_LIMIT`. Escolhidos de outro recorte vêm
   * primeiro e ocupam o lugar dos últimos candidatos, para continuarem à vista; os
   * que já estão no recorte ficam no lugar, sem pular para o topo ao serem tocados.
   */
  const visibleBooks = computed(() => {
    const candidateIds = new Set(candidates.value.map((book) => book.id))
    const kept = selectedBooks.value.filter(
      (book) => draft.value.seedBookIds.includes(book.id) && !candidateIds.has(book.id),
    )
    return [...kept, ...candidates.value].slice(0, CANDIDATE_LIMIT)
  })

  // Pré-preenche com as preferências salvas, ignorando ids que saíram do acervo.
  function prefillFromPreferences(seedBooks: Book[]): void {
    const saved = preferences.value
    if (!saved) {
      return
    }
    const keep = (ids: readonly string[], valid: { id: string }[]) =>
      ids.filter((id) => valid.some((item) => item.id === id))

    selectedBooks.value = seedBooks
    draft.value = {
      areaIds: keep(saved.areaIds, areas.value),
      courseIds: keep(saved.courseIds, courses.value),
      seedBookIds: keep(saved.seedBookIds, seedBooks).slice(0, REQUIRED_SEED_BOOKS),
    }
  }

  async function load(): Promise<void> {
    status.value = 'loading'
    try {
      const [loadedAreas, loadedCourses, loadedGenres, seedBooks] = await Promise.all([
        getKnowledgeAreas(),
        getCourses(),
        getLiteraryGenres(),
        getBooksByIds(preferences.value?.seedBookIds ?? []),
      ])
      areas.value = loadedAreas
      courses.value = loadedCourses
      genres.value = loadedGenres
      prefillFromPreferences(seedBooks)
      status.value = 'ready'
    } catch {
      status.value = 'error'
    }
  }

  /** O que a API recebe para cada recorte. */
  function interestsFor(filter: CandidateFilter): CandidateInterests {
    if (filter.kind === 'genre') {
      return { genreIds: [filter.id], areaIds: [], courseIds: [] }
    }
    if (filter.kind === 'area') {
      return { genreIds: [], areaIds: [filter.id], courseIds: draft.value.courseIds }
    }
    return {
      genreIds: genres.value.map((genre) => genre.id),
      areaIds: draft.value.areaIds,
      courseIds: draft.value.courseIds,
    }
  }

  let candidatesController: AbortController | null = null

  async function loadCandidates(): Promise<void> {
    const filter = activeFilter.value
    const key = filterKey(filter)
    if (candidatesByFilter.value.has(key)) {
      candidatesStatus.value = 'ready'
      return
    }
    candidatesController?.abort()
    candidatesController = new AbortController()
    candidatesStatus.value = 'loading'
    try {
      const loaded = await getOnboardingCandidates(interestsFor(filter), candidatesController.signal)
      candidatesByFilter.value = new Map(candidatesByFilter.value).set(key, loaded)
      candidatesStatus.value = 'ready'
    } catch (error) {
      if (!isCancel(error)) {
        candidatesStatus.value = 'error'
      }
    }
  }

  function selectFilter(filter: CandidateFilter): void {
    activeFilter.value = filter
  }

  /** Esquece a mistura "Todos", que depende das áreas e dos cursos escolhidos. */
  function forgetMixedCandidates(): void {
    const next = new Map(candidatesByFilter.value)
    next.delete(filterKey(ALL_CANDIDATES))
    candidatesByFilter.value = next
  }

  function toggleArea(areaId: string): void {
    const areaIds = toggleValue(draft.value.areaIds, areaId)
    const courseIds = draft.value.courseIds.filter((courseId) =>
      courses.value.some((course) => course.id === courseId && areaIds.includes(course.areaId)),
    )
    draft.value = { ...draft.value, areaIds, courseIds }
    // Sai do recorte de uma área que deixou de ser escolhida.
    if (activeFilter.value.kind === 'area' && !areaIds.includes(activeFilter.value.id)) {
      selectFilter(ALL_CANDIDATES)
    }
  }

  /** Alterna um curso; ao marcá-lo, também marca a área a que ele pertence. */
  function toggleCourse(courseId: string): void {
    const courseIds = toggleValue(draft.value.courseIds, courseId)
    const areaId = courses.value.find((course) => course.id === courseId)?.areaId
    const areaIds =
      areaId && courseIds.includes(courseId) && !draft.value.areaIds.includes(areaId)
        ? [...draft.value.areaIds, areaId]
        : draft.value.areaIds
    draft.value = { ...draft.value, areaIds, courseIds }
  }

  /** Alterna um título; ignora novas escolhas quando o limite já foi atingido. */
  function toggleBook(bookId: string): void {
    const isSelected = draft.value.seedBookIds.includes(bookId)
    if (!isSelected && isComplete.value) {
      return
    }
    const book = visibleBooks.value.find((item) => item.id === bookId)
    if (!isSelected && book && !selectedBooks.value.some((item) => item.id === bookId)) {
      selectedBooks.value = [...selectedBooks.value, book]
    }
    draft.value = { ...draft.value, seedBookIds: toggleValue(draft.value.seedBookIds, bookId) }
  }

  /** Salva o rascunho como preferências, com os gêneros deduzidos dos títulos. */
  function finish(): boolean {
    if (!isComplete.value) {
      return false
    }
    const chosen = selectedBooks.value.filter((book) => draft.value.seedBookIds.includes(book.id))
    const genreIds = inferGenreIds(chosen, genres.value.map((genre) => genre.id))
    save({ ...draft.value, genreIds })
    return true
  }

  // Áreas e cursos que compõem a mistura "Todos".
  const mixKey = computed(() => `${draft.value.areaIds.join(',')}|${draft.value.courseIds.join(',')}`)

  // Busca o recorte atual quando as opções terminam de carregar, a cada troca de
  // recorte e quando áreas ou cursos mudam (a mistura guardada deixa de valer).
  watch([status, activeFilter, mixKey], ([loadStatus, , mix], [, , previousMix]) => {
    if (mix !== previousMix) {
      forgetMixedCandidates()
    }
    if (loadStatus === 'ready') {
      void loadCandidates()
    }
  })

  onUnmounted(() => candidatesController?.abort())

  return {
    status,
    genres,
    areas,
    coursesByLevel,
    selectedAreas,
    selectedCourses,
    draft,
    activeFilter,
    visibleBooks,
    candidatesStatus,
    isComplete,
    missingBooks,
    load,
    loadCandidates,
    selectFilter,
    toggleArea,
    toggleCourse,
    toggleBook,
    finish,
  }
}
