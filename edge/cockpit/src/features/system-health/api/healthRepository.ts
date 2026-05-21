import { http } from '../../../shared/lib/http'
import { ServicesHealthSchema } from '../../../entities/system-health/dtos/ServicesHealthDto'
import type { ServicesHealth } from '../../../entities/system-health/dtos/ServicesHealthDto'

export async function getLiveness(): Promise<boolean> {
  try {
    await http.get('/health/live')
    return true
  } catch {
    return false
  }
}

export async function getServicesHealth(): Promise<ServicesHealth> {
  const res = await http.get('/health/services')
  return ServicesHealthSchema.parse(res.data)
}
