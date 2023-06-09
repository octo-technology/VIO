import axios from 'axios'

class ConfigApiService {
  constructor({ configApiHost }) {
    this.configApiHost = configApiHost
  }

  get api() {
    return axios.create({
      baseURL: `${this.configApiHost}/api/v1`,
      timeout: 20000,
      headers: {
        Accept: 'application/json',
        'Content-Type': 'application/json'
      }
    })
  }

  async getConfigs() {
    const response = await this.api.get('/configs')
    return response.data
  }

  async getInventory() {
    const response = await this.api.get('/inventory')
    return response.data
  }

  async getActiveConfig(configName) {
    const body = { config_name: configName }
    const response = await this.api.post('/configs/active', body)
    return response
  }
}

export default ConfigApiService
