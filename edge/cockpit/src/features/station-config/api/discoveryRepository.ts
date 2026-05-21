import { http } from '../../../shared/lib/http'
import {
  CamerasAvailableSchema,
  ModelsAvailableSchema,
  ConfigOptionsSchema,
  ModelMetadataSchema,
} from '../../../entities/station-config/dtos/DiscoveryDto'
import type {
  CamerasAvailable,
  ModelsAvailable,
  ConfigOptions,
  ModelMetadata,
} from '../../../entities/station-config/dtos/DiscoveryDto'

export async function getCamerasAvailable(): Promise<CamerasAvailable> {
  const res = await http.get('/cameras/available')
  return CamerasAvailableSchema.parse(res.data)
}

export async function getModelsAvailable(): Promise<ModelsAvailable> {
  const res = await http.get('/models/available')
  return ModelsAvailableSchema.parse(res.data)
}

export async function getConfigOptions(): Promise<ConfigOptions> {
  const res = await http.get('/configs/options')
  return ConfigOptionsSchema.parse(res.data)
}

export async function getModelMetadata(servingUrl: string, modelName: string): Promise<ModelMetadata> {
  const res = await http.get(
    `/models/metadata?serving_url=${encodeURIComponent(servingUrl)}&model_name=${encodeURIComponent(modelName)}`,
  )
  return ModelMetadataSchema.parse(res.data)
}
