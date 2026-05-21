import { describe, it, expect } from 'vitest'
import { itemRuleText } from '../itemRuleFormatter'

describe('itemRuleText', () => {
  it('returns null for null rule', () => expect(itemRuleText(null)).toBeNull())
  it('returns null for undefined', () => expect(itemRuleText(undefined)).toBeNull())

  it('formats min_threshold_rule', () => {
    expect(itemRuleText({ item_rule_type: 'min_threshold_rule', threshold: 2, expected_decision: 'OK' }))
      .toBe('≥ 2 camera(s) must return "OK"')
  })

  it('formats min_threshold_ratio_rule', () => {
    expect(itemRuleText({ item_rule_type: 'min_threshold_ratio_rule', threshold: 0.75, expected_decision: 'OK' }))
      .toBe('≥ 75% of cameras must return "OK"')
  })
})
