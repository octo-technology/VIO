import Api from '@/services/api'

class ConfigService {
  async get_configs() {
    return await Api().get('/configs')
  }

  async get_inventory() {
    return await Api().get('/inventory')
  }

  async set_active_config(config_name) {
    const body = { config_name }
    return await Api().post('/configs/active', body)
  }
}

export default new ConfigService()
