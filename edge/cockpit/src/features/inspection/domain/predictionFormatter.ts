export interface ClassPrediction {
  prediction_type: 'class'
  label: string
  probability: number
}

export interface ObjectDetectionPrediction {
  prediction_type: 'objects'
  detected_objects: Record<string, { label: string; objectness: number; location: number[] }>
}

export type Prediction = ClassPrediction | ObjectDetectionPrediction

export function predictionText(pred: Prediction | null | undefined): string {
  if (!pred) return '—'
  if (pred.prediction_type === 'class') {
    return `${pred.label} (${(pred.probability * 100).toFixed(1)}%)`
  }
  return `${Object.keys(pred.detected_objects ?? {}).length} object(s)`
}
