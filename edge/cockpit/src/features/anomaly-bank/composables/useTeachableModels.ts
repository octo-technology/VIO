import { computed } from 'vue'
import { useQuery } from '@tanstack/vue-query'
import * as referenceBankRepository from '../api/referenceBankRepository'

export function useTeachableModels() {
  const { data, isPending: isLoading, refetch } = useQuery({
    queryKey: ['teachable-models'],
    queryFn: referenceBankRepository.getTeachableModels,
  })

  return {
    models: computed(() => data.value ?? []),
    isLoading,
    refetch,
  }
}
