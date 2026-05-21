import { computed } from 'vue'
import { useQuery, useQueryClient } from '@tanstack/vue-query'
import * as configRepository from '../api/configRepository'

export function useConfigs() {
  const queryClient = useQueryClient()

  const { data, isPending: isLoading } = useQuery({
    queryKey: ['configs'],
    queryFn: configRepository.getConfigs,
  })

  async function invalidate() {
    await queryClient.invalidateQueries({ queryKey: ['configs'] })
  }

  return {
    configs: computed(() => data.value ?? []),
    isLoading,
    invalidate,
  }
}
