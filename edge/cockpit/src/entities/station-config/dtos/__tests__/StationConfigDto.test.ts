import { describe, it, expect } from 'vitest'
import { StationConfigSchema } from '../StationConfigDto'

const VALID_CONFIG = {
  station_name: 'test_station',
  camera_configs: {
    cam_1: { camera_id: 'cam_1', camera_type: 'http', service_url: 'http://localhost:8001' },
  },
  pipeline_steps: {
    step_1: {
      camera_id: 'cam_1',
      model_forwarder_config: { model_name: 'my_model', model_serving_url: 'http://localhost:8501' },
    },
  },
  binary_storage_config: { storage_type: 'filesystem', target_directory: 'data' },
  metadata_storage_config: { storage_type: 'filesystem', target_directory: 'data' },
}

describe('StationConfigSchema', () => {
  it('parses a complete valid config', () => {
    const result = StationConfigSchema.safeParse(VALID_CONFIG)
    expect(result.success).toBe(true)
  })

  it('accepts item_rule_config: null', () => {
    const result = StationConfigSchema.safeParse({ ...VALID_CONFIG, item_rule_config: null })
    expect(result.success).toBe(true)
  })

  it('accepts a missing item_rule_config field (optional)', () => {
    const { item_rule_config: _, ...without } = { ...VALID_CONFIG, item_rule_config: undefined }
    const result = StationConfigSchema.safeParse(without)
    expect(result.success).toBe(true)
  })

  it('accepts bucket_name: null in storage config', () => {
    const config = {
      ...VALID_CONFIG,
      binary_storage_config: { storage_type: 'filesystem', target_directory: 'data', bucket_name: null },
    }
    const result = StationConfigSchema.safeParse(config)
    expect(result.success).toBe(true)
  })

  it('accepts a full item_rule_config object', () => {
    const config = {
      ...VALID_CONFIG,
      item_rule_config: { item_rule_type: 'min_threshold_rule', expected_decision: 'OK', threshold: 3 },
    }
    const result = StationConfigSchema.safeParse(config)
    expect(result.success).toBe(true)
  })

  it('accepts camera_configs and pipeline_steps as records (z.record regression)', () => {
    const config = {
      ...VALID_CONFIG,
      camera_configs: {
        cam_a: { camera_id: 'cam_a', camera_type: 'http', service_url: 'http://a' },
        cam_b: { camera_id: 'cam_b', camera_type: 'http', service_url: 'http://b' },
      },
      pipeline_steps: {
        step_a: {
          camera_id: 'cam_a',
          model_forwarder_config: { model_name: 'model', model_serving_url: 'http://s' },
        },
        step_b: {
          camera_id: 'cam_b',
          model_forwarder_config: { model_name: 'model2', model_serving_url: 'http://s' },
        },
      },
    }
    const result = StationConfigSchema.safeParse(config)
    expect(result.success).toBe(true)
  })

  it('accepts a pipeline step with an optional camera_rule_config', () => {
    const config = {
      ...VALID_CONFIG,
      pipeline_steps: {
        step_1: {
          camera_id: 'cam_1',
          model_forwarder_config: { model_name: 'model', model_serving_url: 'http://s' },
          camera_rule_config: { camera_rule_type: 'expected_label_rule', expected_class: 'cat' },
        },
      },
    }
    const result = StationConfigSchema.safeParse(config)
    expect(result.success).toBe(true)
  })

  it('rejects a config missing station_name', () => {
    const { station_name: _, ...without } = VALID_CONFIG
    const result = StationConfigSchema.safeParse(without)
    expect(result.success).toBe(false)
  })

  it('rejects a config missing binary_storage_config', () => {
    const { binary_storage_config: _, ...without } = VALID_CONFIG
    const result = StationConfigSchema.safeParse(without)
    expect(result.success).toBe(false)
  })
})
