import { onMounted, ref } from 'vue'
import { useReadingPreferences } from '../../../composables/useReadingPreferences'
import type { KnowledgeArea } from '../../../models/taxonomy'
import type { Shelf } from '../models/recommendation'
import { getHomeRecommendations } from '../services/recommendation-service'
import { loadShuffleSeed, renewShuffleSeed } from '../services/shuffle-seed-storage'

type LoadStatus = 'loading' | 'ready' | 'error'

/**
 * Carrega as prateleiras de recomendação a partir das preferências salvas.
 *
 * As prateleiras usam a semente de sorteio da sessão: continuam as mesmas quando
 * o visitante volta à home e mudam numa visita nova ou com `shuffle`.
 *
 * @returns Estado de carregamento, prateleiras, áreas escolhidas, `reload` para
 * tentar novamente após erro e `shuffle` para ver outras sugestões.
 */
export function useHomeRecommendations() {
  const { preferences } = useReadingPreferences()

  const status = ref<LoadStatus>('loading')
  const shelves = ref<Shelf[]>([])
  const areas = ref<KnowledgeArea[]>([])
  let shuffleSeed = loadShuffleSeed()

  async function reload(): Promise<void> {
    const profile = preferences.value
    if (!profile) {
      status.value = 'error'
      return
    }
    status.value = 'loading'
    try {
      const result = await getHomeRecommendations(profile, shuffleSeed)
      shelves.value = result.shelves
      areas.value = result.areas
      status.value = 'ready'
    } catch {
      status.value = 'error'
    }
  }

  async function shuffle(): Promise<void> {
    shuffleSeed = renewShuffleSeed()
    await reload()
  }

  onMounted(reload)

  return {
    status,
    shelves,
    areas,
    reload,
    shuffle,
  }
}
