import { z } from 'zod'

const ClassPredictionSchema = z.object({
  prediction_type: z.literal('class'),
  label: z.string(),
  probability: z.number(),
})

const ObjectDetectionPredictionSchema = z.object({
  prediction_type: z.literal('objects'),
  detected_objects: z.record(
    z.string(),
    z.object({
      label: z.string(),
      objectness: z.number(),
      location: z.array(z.number()),
    }),
  ),
})

const PredictionSchema = z.discriminatedUnion('prediction_type', [
  ClassPredictionSchema,
  ObjectDetectionPredictionSchema,
])

export const ItemSchema = z.object({
  id: z.string(),
  creation_date: z.string().optional(),
  state: z.string(),
  decision: z.string().nullable().optional(),
  cameras_metadata: z.record(z.string(), z.unknown()).optional().default({}),
  predictions: z.record(z.string(), PredictionSchema).optional().default({}),
})

export type Item = z.infer<typeof ItemSchema>
export type Prediction = z.infer<typeof PredictionSchema>
export type ClassPrediction = z.infer<typeof ClassPredictionSchema>
export type ObjectDetectionPrediction = z.infer<typeof ObjectDetectionPredictionSchema>

export const ItemListSchema = z.array(ItemSchema)

export const TriggerResponseSchema = z.object({
  item_id: z.string(),
})
export type TriggerResponse = z.infer<typeof TriggerResponseSchema>
