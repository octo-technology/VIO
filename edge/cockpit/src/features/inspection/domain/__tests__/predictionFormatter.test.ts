import { describe, it, expect } from 'vitest'
import { predictionText } from '../predictionFormatter'

describe('predictionText', () => {
  it('returns em dash for null', () => {
    expect(predictionText(null)).toBe('—')
  })

  it('returns em dash for undefined', () => {
    expect(predictionText(undefined)).toBe('—')
  })

  it('formats classification prediction with probability', () => {
    expect(predictionText({ prediction_type: 'class', label: 'OK', probability: 0.987 })).toBe('OK (98.7%)')
  })

  it('formats object detection prediction with object count', () => {
    const pred = {
      prediction_type: 'objects' as const,
      detected_objects: { a: { label: 'cat', objectness: 0.9, location: [0, 0, 1, 1] } },
    }
    expect(predictionText(pred)).toBe('1 object(s)')
  })

  it('formats object detection with zero objects', () => {
    expect(predictionText({ prediction_type: 'objects', detected_objects: {} })).toBe('0 object(s)')
  })
})
