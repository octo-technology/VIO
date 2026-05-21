import { ref } from 'vue'
import { useQueryClient } from '@tanstack/vue-query'
import * as inspectionRepository from '../api/inspectionRepository'
import type { Item } from '../../../entities/inspection/dtos/ItemDto'

export function useTrigger() {
  const queryClient = useQueryClient()
  const triggering = ref(false)
  const polling = ref(false)

  async function triggerInspection(callbacks: {
    onPending: (itemId: string) => void
    onUpdate: (item: Item) => void
  }): Promise<void> {
    triggering.value = true
    try {
      const { item_id: itemId } = await inspectionRepository.trigger()
      if (!itemId) throw new Error('No item_id returned by trigger')

      callbacks.onPending(itemId)

      polling.value = true
      const deadline = Date.now() + 30_000
      while (Date.now() < deadline) {
        try {
          const item = await inspectionRepository.getItem(itemId)
          callbacks.onUpdate(item)
          if (item.state === 'DONE' || item.state === 'ERROR') break
        } catch {
          // item not yet persisted — keep polling
        }
        await new Promise((r) => setTimeout(r, 500))
      }
      polling.value = false

      await queryClient.invalidateQueries({ queryKey: ['items'] })
    } finally {
      triggering.value = false
    }
  }

  return { triggering, polling, triggerInspection }
}
