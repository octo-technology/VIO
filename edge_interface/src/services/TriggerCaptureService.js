import Api from '@/services/api'

class TriggerCaptureService {
  trigger() {
    return Api().post('/trigger')
  }
}

export default new TriggerCaptureService()
