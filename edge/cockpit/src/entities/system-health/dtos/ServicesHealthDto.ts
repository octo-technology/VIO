import { z } from 'zod'

const ServiceInfoSchema = z.object({
  service_type: z.string(),
  ok: z.boolean(),
})

export const ServicesHealthSchema = z.object({
  services: z.record(z.string(), ServiceInfoSchema),
})

export type ServicesHealth = z.infer<typeof ServicesHealthSchema>
export type ServiceInfo = z.infer<typeof ServiceInfoSchema>
