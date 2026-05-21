import { describe, it, expect } from 'vitest'
import { cameraRuleText, cameraRuleResult } from '../cameraRuleEvaluator'

const classPred = { prediction_type: 'class' as const, label: 'OK', probability: 0.99 }
const objectsPred = {
  prediction_type: 'objects' as const,
  detected_objects: {
    a: { label: 'pin', objectness: 0.9, location: [0, 0, 1, 1] },
    b: { label: 'pin', objectness: 0.8, location: [0.1, 0.1, 0.5, 0.5] },
    c: { label: 'bolt', objectness: 0.7, location: [0.5, 0.5, 1, 1] },
  },
}

describe('cameraRuleText', () => {
  it('returns null for null rule', () => expect(cameraRuleText(null)).toBeNull())
  it('formats expected_label_rule', () => expect(cameraRuleText({ camera_rule_type: 'expected_label_rule', expected_class: 'OK' })).toBe('Expects "OK"'))
  it('formats unexpected_label_rule', () => expect(cameraRuleText({ camera_rule_type: 'unexpected_label_rule', unexpected_class: 'NG' })).toBe('Rejects if "NG"'))
  it('formats min_nb_objects_rule', () => expect(cameraRuleText({ camera_rule_type: 'min_nb_objects_rule', class_to_detect: 'pin', threshold: 3 })).toBe('≥ 3 "pin"'))
  it('formats max_nb_objects_rule', () => expect(cameraRuleText({ camera_rule_type: 'max_nb_objects_rule', class_to_detect: 'pin', threshold: 2 })).toBe('≤ 2 "pin"'))
})

describe('cameraRuleResult', () => {
  it('returns null for missing rule or pred', () => {
    expect(cameraRuleResult(null, classPred)).toBeNull()
    expect(cameraRuleResult({ camera_rule_type: 'expected_label_rule', expected_class: 'OK' }, null)).toBeNull()
  })

  describe('expected_label_rule', () => {
    const rule = { camera_rule_type: 'expected_label_rule' as const, expected_class: 'OK' }
    it('returns OK when label matches', () => expect(cameraRuleResult(rule, classPred)).toBe('OK'))
    it('returns KO when label differs', () => expect(cameraRuleResult(rule, { ...classPred, label: 'KO' })).toBe('KO'))
  })

  describe('unexpected_label_rule', () => {
    const rule = { camera_rule_type: 'unexpected_label_rule' as const, unexpected_class: 'NG' }
    it('returns OK when label is not the unexpected class', () => expect(cameraRuleResult(rule, classPred)).toBe('OK'))
    it('returns KO when label is the unexpected class', () => expect(cameraRuleResult(rule, { ...classPred, label: 'NG' })).toBe('KO'))
  })

  describe('min_nb_objects_rule', () => {
    const rule = { camera_rule_type: 'min_nb_objects_rule' as const, class_to_detect: 'pin', threshold: 2 }
    it('returns OK when count >= threshold', () => expect(cameraRuleResult(rule, objectsPred)).toBe('OK'))
    it('returns KO when count < threshold', () => expect(cameraRuleResult({ ...rule, threshold: 3 }, objectsPred)).toBe('KO'))
  })

  describe('max_nb_objects_rule', () => {
    const rule = { camera_rule_type: 'max_nb_objects_rule' as const, class_to_detect: 'pin', threshold: 2 }
    it('returns OK when count <= threshold', () => expect(cameraRuleResult(rule, objectsPred)).toBe('OK'))
    it('returns KO when count > threshold', () => expect(cameraRuleResult({ ...rule, threshold: 1 }, objectsPred)).toBe('KO'))
  })
})
