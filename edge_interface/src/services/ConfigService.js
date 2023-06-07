import Api from '@/services/api.js'

class ConfigService {
  async getConfigs() {
    const configs = await Api().get('/configs')
    return configs
  }

  async getInventory() {
    const inventory = await Api().get('/inventory')
    return inventory
  }

  async setActiveConfig(configName) {
    const body = { config_name: configName }
    const activeConfig = await Api().post('/configs/active', body)
    return activeConfig
  }
  async get_active_config(config_name) {
    return await Api().get("/configs/active");
  }
}

export default new ConfigService()
