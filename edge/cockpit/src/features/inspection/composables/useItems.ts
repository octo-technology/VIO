import { computed, type Ref } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import * as inspectionRepository from '../api/inspectionRepository'

export function useItems(options?: { enabled?: Ref<boolean> }) {
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['items'],
    queryFn: inspectionRepository.getItems,
    enabled: options?.enabled,
    retry: false,
  })

  async function fetchItem(id: string) {
    return inspectionRepository.getItem(id)
  }

  function itemImageUrl(itemId: string, cameraId: string): string {
    return inspectionRepository.getItemImageUrl(itemId, cameraId)
  }

  return {
    items: computed(() => data.value ?? []),
    isLoading,
    refetch,
    fetchItem,
    itemImageUrl,
  }
}
