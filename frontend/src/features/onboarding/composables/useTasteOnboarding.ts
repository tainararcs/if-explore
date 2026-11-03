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
  canCompleteAreas,
  canCompleteBooks,
  furthestReachableStep,
  toggleValue,
  type OnboardingDraft,
} from '../models/onboarding-draft'
import { getOnboardingCandidates } from '../services/onboarding-service'

type LoadStatus = 'loading' | 'ready' | 'error'

// Espera a pessoa terminar de marcar áreas e cursos antes de buscar os candidatos.
const CANDIDATES_DEBOUNCE_MS = 300

/**
 * Concentra o estado do onboarding: opções do acervo, rascunho das escolhas,
 * regras de cada passo e a gravação final das preferências.
 *
 * Os títulos candidatos vêm da API e são recarregados quando mudam as áreas ou
 * os cursos. Títulos já escolhidos continuam selecionados e visíveis mesmo que
 * deixem de ser candidatos.
 *
 * O rascunho só vira preferência salva em `finish()`; sair no meio do fluxo
 * não altera as preferências existentes.
 */
export function useTasteOnboarding() {
  const { preferences, save } = useReadingPreferences()

  const status = ref<LoadStatus>('loading')
  const areas = ref<KnowledgeArea[]>([])
  const courses = ref<Course[]>([])
  const genres = ref<LiteraryGenre[]>([])
  const candidates = ref<Book[]>([])
  const candidatesStatus = ref<LoadStatus>('loading')
  // Livros já escolhidos, para que continuem visíveis fora dos candidatos atuais.
  const selectedBooks = ref<Book[]>([])

  const draft = ref<OnboardingDraft>({
    areaIds: [],
    courseIds: [],
    seedBookIds: [],
    genreIds: [],
  })

  /** Escolhidos que não estão entre os candidatos vêm primeiro; depois, os candidatos. */
  const candidateBooks = computed(() => {
    const candidateIds = new Set(candidates.value.map((book) => book.id))
    const kept = selectedBooks.value.filter(
      (book) => draft.value.seedBookIds.includes(book.id) && !candidateIds.has(book.id),
    )
    return [...kept, ...candidates.value]
  })
  const canLeaveAreas = computed(() => canCompleteAreas(draft.value))
  const isBooksComplete = computed(() => canCompleteBooks(draft.value))
  const furthestStep = computed(() => furthestReachableStep(draft.value))
  const missingBooks = computed(() => REQUIRED_SEED_BOOKS - draft.value.seedBookIds.length)

  /** Todos os cursos do campus agrupados por nível de ensino, sem níveis vazios. */
  const coursesByLevel = computed(() =>
    COURSE_LEVELS.map((level) => ({
      level,
      courses: courses.value.filter((course) => course.level === level),
    })).filter((group) => group.courses.length > 0),
  )

  // Pré-preenche com as preferências salvas, ignorando ids que saíram do acervo.
  function prefillFromPreferences(seedBooks: Book[]): void {
    const saved = preferences.value
    if (!saved) {
      return
    }
    const keep = (ids: readonly string[], valid: { id: string }[]) =>
      ids.filter((id) => valid.some((item) => item.id === id))

    const seedBookIds = keep(saved.seedBookIds, seedBooks)
    selectedBooks.value = seedBooks
    draft.value = {
      areaIds: keep(saved.areaIds, areas.value),
      courseIds: keep(saved.courseIds, courses.value),
      seedBookIds: seedBookIds.slice(0, REQUIRED_SEED_BOOKS),
      genreIds: keep(saved.genreIds, genres.value),
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

  function toggleArea(areaId: string): void {
    const areaIds = toggleValue(draft.value.areaIds, areaId)
    const courseIds = draft.value.courseIds.filter((courseId) =>
      courses.value.some((course) => course.id === courseId && areaIds.includes(course.areaId)),
    )
    draft.value = { ...draft.value, areaIds, courseIds }
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
    if (!isSelected && isBooksComplete.value) {
      return
    }
    const book = candidateBooks.value.find((item) => item.id === bookId)
    if (!isSelected && book && !selectedBooks.value.some((item) => item.id === bookId)) {
      selectedBooks.value = [...selectedBooks.value, book]
    }
    draft.value = { ...draft.value, seedBookIds: toggleValue(draft.value.seedBookIds, bookId) }
  }

  function toggleGenre(genreId: string): void {
    draft.value = { ...draft.value, genreIds: toggleValue(draft.value.genreIds, genreId) }
  }

  /** Salva o rascunho como preferências; exige os passos obrigatórios completos. */
  function finish(): boolean {
    if (!canLeaveAreas.value || !isBooksComplete.value) {
      return false
    }
    save({ ...draft.value })
    return true
  }

  let candidatesController: AbortController | null = null

  async function loadCandidates(): Promise<void> {
    candidatesController?.abort()
    candidatesController = new AbortController()
    candidatesStatus.value = 'loading'
    try {
      candidates.value = await getOnboardingCandidates(
        draft.value.areaIds,
        draft.value.courseIds,
        candidatesController.signal,
      )
      candidatesStatus.value = 'ready'
    } catch (error) {
      if (!isCancel(error)) {
        candidatesStatus.value = 'error'
      }
    }
  }

  // Recarrega os candidatos quando mudam as áreas ou os cursos, depois de carregar as
  // opções. Sem área escolhida não há passo de títulos, então não há o que buscar.
  watch(
    [status, () => draft.value.areaIds, () => draft.value.courseIds],
    ([loadStatus, areaIds], _previous, onCleanup) => {
      if (loadStatus !== 'ready' || areaIds.length === 0) {
        return
      }
      const timer = window.setTimeout(() => void loadCandidates(), CANDIDATES_DEBOUNCE_MS)
      onCleanup(() => window.clearTimeout(timer))
    },
  )

  onUnmounted(() => candidatesController?.abort())

  return {
    status,
    areas,
    genres,
    draft,
    candidateBooks,
    candidatesStatus,
    loadCandidates,
    coursesByLevel,
    canLeaveAreas,
    isBooksComplete,
    furthestStep,
    missingBooks,
    load,
    toggleArea,
    toggleCourse,
    toggleBook,
    toggleGenre,
    finish,
  }
}
