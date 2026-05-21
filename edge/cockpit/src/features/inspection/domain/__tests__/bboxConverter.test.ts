import { describe, it, expect } from 'vitest'
import { bboxPct } from '../bboxConverter'

describe('bboxPct', () => {
  it('converts SSD format [y_min, x_min, y_max, x_max]', () => {
    const result = bboxPct([0.1, 0.2, 0.5, 0.8], { model_forwarder_config: { model_name: 'ssd_mobilenet' } })
    expect(result).toEqual({ x: 20, y: 10, w: 60, h: 40 })
  })

  it('converts YOLO format [x_min, y_min, x_max, y_max]', () => {
    const result = bboxPct([0.2, 0.1, 0.8, 0.5], { model_forwarder_config: { model_name: 'yolov8' } })
    expect(result).toEqual({ x: 20, y: 10, w: 60, h: 40 })
  })

  it('handles null step gracefully (defaults to SSD)', () => {
    const result = bboxPct([0.1, 0.2, 0.5, 0.8], null)
    expect(result).toEqual({ x: 20, y: 10, w: 60, h: 40 })
  })

  it('detects yolo by name substring (case-insensitive)', () => {
    // YOLO_v5 uppercase → treated as YOLO → [x_min, y_min, x_max, y_max]
    const result = bboxPct([0.2, 0.1, 0.8, 0.5], { model_forwarder_config: { model_name: 'YOLO_v5' } })
    expect(result).toEqual({ x: 20, y: 10, w: 60, h: 40 })
  })
})
