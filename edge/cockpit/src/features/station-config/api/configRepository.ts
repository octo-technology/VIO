import { http } from '../../../shared/lib/http'
import { StationConfigSchema } from '../../../entities/station-config/dtos/StationConfigDto'
import type { StationConfig } from '../../../entities/station-config/dtos/StationConfigDto'

export async function getConfigs(): Promise<StationConfig[]> {
  const res = await http.get('/configs')
  return Object.values(res.data).map((cfg) => StationConfigSchema.parse(cfg))
}

export async function getActiveConfig(): Promise<StationConfig | null> {
  try {
    const res = await http.get('/configs/active')
    return StationConfigSchema.parse(res.data)
  } catch (e: any) {
    if (e?.response?.status === 404) return null
    throw e
  }
}

export async function activateConfig(stationName: string): Promise<void> {
  await http.put('/configs/active', { station_name: stationName })
}

export async function createConfig(config: StationConfig): Promise<void> {
  await http.post('/configs', config)
}

export async function saveConfig(config: StationConfig): Promise<void> {
  await http.put(`/configs/${encodeURIComponent(config.station_name)}`, config)
}

export async function deleteConfig(stationName: string): Promise<void> {
  await http.delete(`/configs/${encodeURIComponent(stationName)}`)
}
