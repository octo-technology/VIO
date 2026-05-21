import { http } from '../../../shared/lib/http'
import { ItemSchema, ItemListSchema, TriggerResponseSchema } from '../../../entities/inspection/dtos/ItemDto'
import type { Item, TriggerResponse } from '../../../entities/inspection/dtos/ItemDto'

export async function getItems(): Promise<Item[]> {
  const res = await http.get('/items')
  return ItemListSchema.parse(res.data)
}

export async function getItem(itemId: string): Promise<Item> {
  const res = await http.get(`/items/${itemId}`)
  return ItemSchema.parse(res.data)
}

export async function trigger(): Promise<TriggerResponse> {
  const res = await http.post('/trigger')
  return TriggerResponseSchema.parse(res.data)
}

export function getItemImageUrl(itemId: string, cameraId: string): string {
  return `${http.defaults.baseURL}/items/${itemId}/binaries/${cameraId}`
}
