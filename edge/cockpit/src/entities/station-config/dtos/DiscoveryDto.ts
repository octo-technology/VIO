import { z } from 'zod'

const CameraInfoSchema = z.object({
  backend: z.string().optional(),
  position: z.string().nullish(),
})

export const CamerasAvailableSchema = z.object({
  cameras: z.record(z.string(), z.record(z.string(), CameraInfoSchema)),
})

export const ModelsAvailableSchema = z.object({
  models: z.record(z.string(), z.array(z.string())),
})

export const ConfigOptionsSchema = z.object({
  camera_rule_types: z.array(z.string()),
  item_rule_types: z.array(z.string()),
  storage_types: z.array(z.string()),
  camera_types: z.array(z.string()),
})

export const ModelMetadataSchema = z.object({
  version: z.string().optional(),
  class_names: z.array(z.string()).optional(),
  output_type: z.string().optional(),
})

export type CamerasAvailable = z.infer<typeof CamerasAvailableSchema>
export type ModelsAvailable = z.infer<typeof ModelsAvailableSchema>
export type ConfigOptions = z.infer<typeof ConfigOptionsSchema>
export type ModelMetadata = z.infer<typeof ModelMetadataSchema>
