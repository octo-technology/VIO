export interface BboxRect {
  x: number
  y: number
  w: number
  h: number
}

interface ModelForwarderConfig {
  model_name?: string
}

interface PipelineStep {
  model_forwarder_config?: ModelForwarderConfig
}

/** Converts a normalized bounding-box location to percentage-based CSS coords.
 *  SSD format: [y_min, x_min, y_max, x_max], YOLO format: [x_min, y_min, x_max, y_max]. */
export function bboxPct(location: number[], step: PipelineStep | null | undefined): BboxRect {
  const isYolo = step?.model_forwarder_config?.model_name?.toLowerCase().includes('yolo') ?? false
  let xMin: number, yMin: number, xMax: number, yMax: number
  if (isYolo) {
    ;[xMin, yMin, xMax, yMax] = location
  } else {
    ;[yMin, xMin, yMax, xMax] = location
  }
  return {
    x: +(xMin * 100).toFixed(2),
    y: +(yMin * 100).toFixed(2),
    w: +((xMax - xMin) * 100).toFixed(2),
    h: +((yMax - yMin) * 100).toFixed(2),
  }
}
