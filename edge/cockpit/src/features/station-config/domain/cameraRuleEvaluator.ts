import type { Prediction } from '../../inspection/domain/predictionFormatter'

export interface ExpectedLabelRule {
  camera_rule_type: 'expected_label_rule'
  expected_class: string
}

export interface UnexpectedLabelRule {
  camera_rule_type: 'unexpected_label_rule'
  unexpected_class: string
}

export interface MinNbObjectsRule {
  camera_rule_type: 'min_nb_objects_rule'
  class_to_detect: string
  threshold: number
}

export interface MaxNbObjectsRule {
  camera_rule_type: 'max_nb_objects_rule'
  class_to_detect: string
  threshold: number
}

export type CameraRule = ExpectedLabelRule | UnexpectedLabelRule | MinNbObjectsRule | MaxNbObjectsRule

export function cameraRuleText(rule: CameraRule | null | undefined): string | null {
  if (!rule) return null
  switch (rule.camera_rule_type) {
    case 'expected_label_rule':   return `Expects "${rule.expected_class}"`
    case 'unexpected_label_rule': return `Rejects if "${rule.unexpected_class}"`
    case 'min_nb_objects_rule':   return `≥ ${rule.threshold} "${rule.class_to_detect}"`
    case 'max_nb_objects_rule':   return `≤ ${rule.threshold} "${rule.class_to_detect}"`
  }
}

export function cameraRuleResult(rule: CameraRule | null | undefined, pred: Prediction | null | undefined): 'OK' | 'KO' | null {
  if (!rule || !pred) return null
  switch (rule.camera_rule_type) {
    case 'expected_label_rule':
      return pred.prediction_type === 'class' && pred.label === rule.expected_class ? 'OK' : 'KO'
    case 'unexpected_label_rule':
      return pred.prediction_type === 'class' && pred.label === rule.unexpected_class ? 'KO' : 'OK'
    case 'min_nb_objects_rule': {
      const objects = pred.prediction_type === 'objects' ? pred.detected_objects : {}
      const n = Object.values(objects).filter(o => o.label === rule.class_to_detect).length
      return n >= rule.threshold ? 'OK' : 'KO'
    }
    case 'max_nb_objects_rule': {
      const objects = pred.prediction_type === 'objects' ? pred.detected_objects : {}
      const n = Object.values(objects).filter(o => o.label === rule.class_to_detect).length
      return n <= rule.threshold ? 'OK' : 'KO'
    }
  }
}
