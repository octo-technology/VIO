import { z } from 'zod'

const CameraRuleSchema = z.object({
  camera_rule_type: z.string(),
  expected_class: z.string().optional(),
  unexpected_class: z.string().optional(),
  class_to_detect: z.string().optional(),
  threshold: z.number().optional(),
})

const ItemRuleSchema = z.object({
  item_rule_type: z.string(),
  expected_decision: z.string(),
  threshold: z.number(),
})

const StorageConfigSchema = z.object({
  storage_type: z.string(),
  target_directory: z.string(),
  bucket_name: z.string().nullable().optional(),
})

const CameraConfigSchema = z.object({
  camera_id: z.string(),
  camera_type: z.string(),
  service_url: z.string(),
})

const ModelForwarderConfigSchema = z.object({
  model_name: z.string(),
  model_version: z.string().optional(),
  model_serving_url: z.string(),
})

const PipelineStepSchema = z.object({
  camera_id: z.string(),
  model_forwarder_config: ModelForwarderConfigSchema,
  camera_rule_config: CameraRuleSchema.nullable().optional(),
})

export const StationConfigSchema = z.object({
  station_name: z.string(),
  camera_configs: z.record(z.string(), CameraConfigSchema),
  pipeline_steps: z.record(z.string(), PipelineStepSchema),
  item_rule_config: ItemRuleSchema.nullable().optional(),
  binary_storage_config: StorageConfigSchema,
  metadata_storage_config: StorageConfigSchema,
})

export type StationConfig = z.infer<typeof StationConfigSchema>
export type PipelineStep = z.infer<typeof PipelineStepSchema>
export type CameraConfig = z.infer<typeof CameraConfigSchema>
export type ModelForwarderConfig = z.infer<typeof ModelForwarderConfigSchema>
