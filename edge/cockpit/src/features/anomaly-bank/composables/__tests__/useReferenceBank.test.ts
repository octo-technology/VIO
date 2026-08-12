import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { defineComponent, h } from 'vue'
import { mount, flushPromises } from '@vue/test-utils'
import { useReferenceBank } from '../useReferenceBank'

vi.mock('../../api/referenceBankRepository', () => ({
  addReferenceImages: vi.fn(),
  getTrainingJob: vi.fn(),
  getTeachableModels: vi.fn(),
}))

import * as referenceBankRepository from '../../api/referenceBankRepository'

const MODEL = 'my_part'
const FILES = [new File([new Uint8Array([1, 2, 3])], 'a.jpg', { type: 'image/jpeg' })]

const ACCEPTED = { job_id: 'job-1', model_name: MODEL, status: 'pending', total: 1, processed: 0 }
const RUNNING = { ...ACCEPTED, status: 'running', processed: 0 }
const COMPLETED = { ...ACCEPTED, status: 'completed', processed: 1, bank_size: 7 }

function mountComposable() {
  let result: any
  const Wrapper = defineComponent({
    setup() {
      result = useReferenceBank()
      return () => h('div')
    },
  })
  mount(Wrapper)
  return () => result
}

beforeEach(() => {
  vi.clearAllMocks()
})

afterEach(() => {
  vi.useRealTimers()
})

describe('useReferenceBank', () => {
  it('starts idle', () => {
    const result = mountComposable()
    expect(result().uploading.value).toBe(false)
    expect(result().job.value).toBeNull()
    expect(result().progress.value).toBe(0)
  })

  it('returns immediately when the job is already completed', async () => {
    ;(referenceBankRepository.addReferenceImages as ReturnType<typeof vi.fn>).mockResolvedValue(COMPLETED)
    const result = mountComposable()

    const job = await result().teach(MODEL, FILES)

    expect(referenceBankRepository.addReferenceImages).toHaveBeenCalledWith(MODEL, FILES)
    expect(job.status).toBe('completed')
    expect(referenceBankRepository.getTrainingJob).not.toHaveBeenCalled()
    expect(result().uploading.value).toBe(false)
  })

  it('polls until the job reaches a terminal status', async () => {
    vi.useFakeTimers()
    ;(referenceBankRepository.addReferenceImages as ReturnType<typeof vi.fn>).mockResolvedValue(ACCEPTED)
    ;(referenceBankRepository.getTrainingJob as ReturnType<typeof vi.fn>)
      .mockResolvedValueOnce(RUNNING)
      .mockResolvedValueOnce(COMPLETED)

    const result = mountComposable()
    const promise = result().teach(MODEL, FILES)

    await vi.advanceTimersByTimeAsync(1200)
    const job = await promise

    expect(referenceBankRepository.getTrainingJob).toHaveBeenCalledTimes(2)
    expect(job.status).toBe('completed')
    expect(result().progress.value).toBe(100)
    expect(result().job.value.bank_size).toBe(7)
  })

  it('keeps polling when a poll rejects transiently', async () => {
    vi.useFakeTimers()
    ;(referenceBankRepository.addReferenceImages as ReturnType<typeof vi.fn>).mockResolvedValue(ACCEPTED)
    ;(referenceBankRepository.getTrainingJob as ReturnType<typeof vi.fn>)
      .mockRejectedValueOnce(new Error('502'))
      .mockResolvedValue(COMPLETED)

    const result = mountComposable()
    const promise = result().teach(MODEL, FILES)

    await vi.advanceTimersByTimeAsync(1200)
    await promise

    expect(referenceBankRepository.getTrainingJob).toHaveBeenCalledTimes(2)
  })

  it('surfaces a failed job without throwing', async () => {
    ;(referenceBankRepository.addReferenceImages as ReturnType<typeof vi.fn>).mockResolvedValue({
      ...ACCEPTED,
      status: 'failed',
      error: 'bad image',
    })
    const result = mountComposable()

    const job = await result().teach(MODEL, FILES)

    expect(job.status).toBe('failed')
    expect(job.error).toBe('bad image')
  })

  it('clears uploading after completion', async () => {
    ;(referenceBankRepository.addReferenceImages as ReturnType<typeof vi.fn>).mockResolvedValue(COMPLETED)
    const result = mountComposable()

    await result().teach(MODEL, FILES)
    await flushPromises()

    expect(result().uploading.value).toBe(false)
  })
})
