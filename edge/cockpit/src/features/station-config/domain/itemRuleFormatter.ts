export interface MinThresholdRule {
  item_rule_type: 'min_threshold_rule'
  threshold: number
  expected_decision: string
}

export interface MinThresholdRatioRule {
  item_rule_type: 'min_threshold_ratio_rule'
  threshold: number
  expected_decision: string
}

export type ItemRule = MinThresholdRule | MinThresholdRatioRule

export function itemRuleText(rule: ItemRule | null | undefined): string | null {
  if (!rule) return null
  switch (rule.item_rule_type) {
    case 'min_threshold_rule':
      return `≥ ${rule.threshold} camera(s) must return "${rule.expected_decision}"`
    case 'min_threshold_ratio_rule':
      return `≥ ${(rule.threshold * 100).toFixed(0)}% of cameras must return "${rule.expected_decision}"`
  }
}
