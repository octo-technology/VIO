import axios from 'axios'

const apiClient = axios.create({
  baseURL: '/api/v1',
  headers: {
    Accept: 'application/json',
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (!error.response) {
      error.message = 'Orchestrator unreachable — check the edge device.'
    }
    return Promise.reject(error)
  }
)

export default {
  // Inspection
  trigger() {
    return apiClient.post('/trigger')
  },
  getItems() {
    return apiClient.get('/items')
  },
  getItem(itemId) {
    return apiClient.get(`/items/${itemId}`)
  },
  getItemImage(itemId, cameraId) {
    return `${apiClient.defaults.baseURL}/items/${itemId}/binaries/${cameraId}`
  },

  // Configuration
  getConfigs() {
    return apiClient.get('/configs')
  },
  getActiveConfig() {
    return apiClient.get('/configs/active')
  },
  setActiveConfig(stationName) {
    return apiClient.post(`/configs/active?station_name=${stationName}`)
  },

  // Health
  getHealth() {
    return apiClient.get('/health/live')
  },
  getServicesHealth() {
    return apiClient.get('/health/services')
  },
}
