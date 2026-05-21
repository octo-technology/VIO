import type { CameraRule } from './cameraRuleEvaluator'

export const CAMERA_RULE_DEFAULTS: Record<string, CameraRule> = {
  expected_label_rule:   { camera_rule_type: 'expected_label_rule', expected_class: '' },
  unexpected_label_rule: { camera_rule_type: 'unexpected_label_rule', unexpected_class: '' },
  min_nb_objects_rule:   { camera_rule_type: 'min_nb_objects_rule', class_to_detect: '', threshold: 1 },
  max_nb_objects_rule:   { camera_rule_type: 'max_nb_objects_rule', class_to_detect: '', threshold: 1 },
}

export const RULE_TYPE_LABELS: Record<string, string> = {
  expected_label_rule: 'Expected label',
  unexpected_label_rule: 'Unexpected label',
  min_nb_objects_rule: 'Min nb objects',
  max_nb_objects_rule: 'Max nb objects',
  min_threshold_rule: 'Min count',
  min_threshold_ratio_rule: 'Min ratio (%)',
}

export const OUTPUT_TYPE_CAMERA_RULES: Record<string, string[]> = {
  classification: ['expected_label_rule', 'unexpected_label_rule'],
  object_detection: ['min_nb_objects_rule', 'max_nb_objects_rule'],
  yolo: ['min_nb_objects_rule', 'max_nb_objects_rule'],
}

export function createDefaultCameraRule(type: string): CameraRule | null {
  return type === 'none' ? null : { ...CAMERA_RULE_DEFAULTS[type] } as CameraRule
}
