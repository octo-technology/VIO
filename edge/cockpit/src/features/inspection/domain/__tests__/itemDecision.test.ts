import { describe, it, expect } from 'vitest'
import { itemChipColor, itemChipLabel } from '../itemDecision'

describe('itemChipColor', () => {
  it('returns error for ERROR state', () => {
    expect(itemChipColor({ id: '1', state: 'ERROR' })).toBe('error')
  })

  it('returns success for DONE + OK decision', () => {
    expect(itemChipColor({ id: '1', state: 'DONE', decision: 'OK' })).toBe('success')
  })

  it('returns error for DONE + KO decision', () => {
    expect(itemChipColor({ id: '1', state: 'DONE', decision: 'KO' })).toBe('error')
  })

  it('returns warning for PENDING state', () => {
    expect(itemChipColor({ id: '1', state: 'PENDING' })).toBe('warning')
  })
})

describe('itemChipLabel', () => {
  it('returns ERROR for ERROR state', () => {
    expect(itemChipLabel({ id: '1', state: 'ERROR' })).toBe('ERROR')
  })

  it('returns decision for DONE state', () => {
    expect(itemChipLabel({ id: '1', state: 'DONE', decision: 'OK' })).toBe('OK')
  })

  it('returns state for in-progress states', () => {
    expect(itemChipLabel({ id: '1', state: 'PENDING' })).toBe('PENDING')
    expect(itemChipLabel({ id: '1', state: 'PROCESSING' })).toBe('PROCESSING')
  })
})
