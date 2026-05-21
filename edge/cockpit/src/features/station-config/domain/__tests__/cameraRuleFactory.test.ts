import { describe, it, expect } from 'vitest'
import { createDefaultCameraRule, CAMERA_RULE_DEFAULTS } from '../cameraRuleFactory'

describe('createDefaultCameraRule', () => {
  it('returns null for "none"', () => {
    expect(createDefaultCameraRule('none')).toBeNull()
  })

  it('returns a copy of the default for expected_label_rule', () => {
    const rule = createDefaultCameraRule('expected_label_rule')
    expect(rule).toEqual({ camera_rule_type: 'expected_label_rule', expected_class: '' })
    expect(rule).not.toBe(CAMERA_RULE_DEFAULTS.expected_label_rule)
  })

  it('returns a copy of the default for min_nb_objects_rule', () => {
    const rule = createDefaultCameraRule('min_nb_objects_rule')
    expect(rule).toEqual({ camera_rule_type: 'min_nb_objects_rule', class_to_detect: '', threshold: 1 })
  })
})
