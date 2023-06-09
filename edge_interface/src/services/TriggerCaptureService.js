import Api from '@/services/api.js'

class TriggerCaptureService {
  trigger() {
    return Api().post('/trigger')
  }
}

export default new TriggerCaptureService()
