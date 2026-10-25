import { computed, ref } from 'vue'
import { useReadingPreferences } from '../../../composables/useReadingPreferences'
import type { Book } from '../../../models/book'
import { REQUIRED_SEED_BOOKS } from '../../../models/reading-preferences'
import type { Course, KnowledgeArea, LiteraryGenre } from '../../../models/taxonomy'
import {
  getBooks,
  getCourses,
  getKnowledgeAreas,
  getLiteraryGenres,
} from '../../../services/catalog-service'
import {
  canCompleteAreas,
  canCompleteBooks,
  furthestReachableStep,
  rankCandidateBooks,
  toggleValue,
  type OnboardingDraft,
} from '../models/onboarding-draft'

type LoadStatus = 'loading' | 'ready' | 'error'

/**
 * Concentra o estado do onboarding: opções do acervo, rascunho das escolhas,
 * regras de cada passo e a gravação final das preferências.
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
  const books = ref<Book[]>([])

  const draft = ref<OnboardingDraft>({
    areaIds: [],
    courseIds: [],
    seedBookIds: [],
    genreIds: [],
  })

  const candidateBooks = computed(() => rankCandidateBooks(books.value, draft.value))
  const canLeaveAreas = computed(() => canCompleteAreas(draft.value))
  const isBooksComplete = computed(() => canCompleteBooks(draft.value))
  const furthestStep = computed(() => furthestReachableStep(draft.value))
  const missingBooks = computed(() => REQUIRED_SEED_BOOKS - draft.value.seedBookIds.length)

  /** Cursos agrupados pelas áreas escolhidas, na ordem das áreas. */
  const coursesBySelectedArea = computed(() =>
    areas.value
      .filter((area) => draft.value.areaIds.includes(area.id))
      .map((area) => ({
        area,
        courses: courses.value.filter((course) => course.areaId === area.id),
      }))
      .filter((group) => group.courses.length > 0),
  )

  // Pré-preenche com as preferências salvas, ignorando ids que saíram do acervo.
  function prefillFromPreferences(): void {
    const saved = preferences.value
    if (!saved) {
      return
    }
    const keep = (ids: readonly string[], valid: { id: string }[]) =>
      ids.filter((id) => valid.some((item) => item.id === id))

    const seedBookIds = keep(saved.seedBookIds, books.value)
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
      const [loadedAreas, loadedCourses, loadedGenres, loadedBooks] = await Promise.all([
        getKnowledgeAreas(),
        getCourses(),
        getLiteraryGenres(),
        getBooks(),
      ])
      areas.value = loadedAreas
      courses.value = loadedCourses
      genres.value = loadedGenres
      books.value = loadedBooks
      prefillFromPreferences()
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
    // Títulos que deixam de ser candidatos saem da seleção para não ficarem invisíveis.
    const candidates = rankCandidateBooks(books.value, { areaIds, courseIds })
    const seedBookIds = draft.value.seedBookIds.filter((id) =>
      candidates.some((book) => book.id === id),
    )
    draft.value = { ...draft.value, areaIds, courseIds, seedBookIds }
  }

  function toggleCourse(courseId: string): void {
    draft.value = { ...draft.value, courseIds: toggleValue(draft.value.courseIds, courseId) }
  }

  /** Alterna um título; ignora novas escolhas quando o limite já foi atingido. */
  function toggleBook(bookId: string): void {
    const isSelected = draft.value.seedBookIds.includes(bookId)
    if (!isSelected && isBooksComplete.value) {
      return
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

  return {
    status,
    areas,
    genres,
    draft,
    candidateBooks,
    coursesBySelectedArea,
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
