import { computed, ref, watch, type Ref } from 'vue'
import type { BookDetail } from '../../../models/book'
import type { Course, KnowledgeArea, LiteraryGenre } from '../../../models/taxonomy'
import {
  getBookById,
  getCourses,
  getKnowledgeAreas,
  getLiteraryGenres,
} from '../../../services/catalog-service'
import type { RelatedShelves } from '../models/related-books'
import { getRelatedBooks } from '../services/book-detail-service'

type LoadStatus = 'loading' | 'ready' | 'notFound' | 'error'

/**
 * Carrega o livro do id informado, os nomes de área, cursos e gêneros e as
 * prateleiras de relacionados. Recarrega quando o id muda (navegação entre
 * livros relacionados) e ignora respostas de ids anteriores.
 *
 * Ao trocar de livro, o anterior continua na tela com `isRefreshing` ativo
 * até o próximo chegar, em vez de voltar ao estado de carregamento. Uma falha
 * só nos relacionados não impede a página: as prateleiras ficam de fora.
 *
 * @param bookId - Id do livro vindo da rota.
 * @returns Estado de carregamento, livro, dados de apoio e `reload`.
 */
export function useBookDetail(bookId: Ref<string>) {
  const status = ref<LoadStatus>('loading')
  const book = ref<BookDetail | null>(null)
  const shelves = ref<RelatedShelves | null>(null)
  const areas = ref<KnowledgeArea[]>([])
  const courses = ref<Course[]>([])
  const genres = ref<LiteraryGenre[]>([])
  const isRefreshing = ref(false)

  let requestId = 0

  async function reload(): Promise<void> {
    const current = ++requestId
    const id = bookId.value
    if (status.value === 'ready') {
      isRefreshing.value = true
    } else {
      status.value = 'loading'
    }
    try {
      const [found, related, allAreas, allCourses, allGenres] = await Promise.all([
        getBookById(id),
        getRelatedBooks(id).catch(() => null),
        getKnowledgeAreas(),
        getCourses(),
        getLiteraryGenres(),
      ])
      if (current !== requestId) {
        return
      }
      book.value = found
      shelves.value = found ? related : null
      areas.value = allAreas
      courses.value = allCourses
      genres.value = allGenres
      status.value = found ? 'ready' : 'notFound'
    } catch {
      if (current === requestId) {
        status.value = 'error'
      }
    } finally {
      if (current === requestId) {
        isRefreshing.value = false
      }
    }
  }

  watch(bookId, reload, { immediate: true })

  const areaName = computed(
    () => areas.value.find((area) => area.id === book.value?.areaId)?.name ?? '',
  )
  const courseNames = computed(() =>
    courses.value
      .filter((course) => book.value?.courseIds.includes(course.id))
      .map((course) => course.name),
  )
  const genreNames = computed(() =>
    genres.value
      .filter((genre) => book.value?.genreIds.includes(genre.id))
      .map((genre) => genre.name),
  )

  return {
    status,
    isRefreshing,
    book,
    areaName,
    courseNames,
    genreNames,
    shelves,
    reload,
  }
}
