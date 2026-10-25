import { onMounted, ref } from 'vue'
import { useReadingPreferences } from '../../../composables/useReadingPreferences'
import type { KnowledgeArea } from '../../../models/taxonomy'
import type { Shelf } from '../models/recommendation'
import { getHomeRecommendations } from '../services/recommendation-service'

type LoadStatus = 'loading' | 'ready' | 'error'

/**
 * Carrega as prateleiras de recomendação a partir das preferências salvas.
 *
 * @returns Estado de carregamento, prateleiras, áreas escolhidas e `reload`
 * para tentar novamente após erro.
 */
export function useHomeRecommendations() {
  const { preferences } = useReadingPreferences()

  const status = ref<LoadStatus>('loading')
  const shelves = ref<Shelf[]>([])
  const areas = ref<KnowledgeArea[]>([])

  async function reload(): Promise<void> {
    const profile = preferences.value
    if (!profile) {
      status.value = 'error'
      return
    }
    status.value = 'loading'
    try {
      const result = await getHomeRecommendations(profile)
      shelves.value = result.shelves
      areas.value = result.areas
      status.value = 'ready'
    } catch {
      status.value = 'error'
    }
  }

  onMounted(reload)

  return {
    status,
    shelves,
    areas,
    reload,
  }
}
