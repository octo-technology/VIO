import Api from "@/services/api";

class ConfigService {
  async get_configs() {
    return await Api().get("/configs");
  }
  async get_inventory() {
    return await Api().get("/inventory");
  }
  async set_active_config(config_name) {
    const body = { config_name: config_name };
    return await Api().post("/configs/active", body);
  }
  async get_active_config(config_name) {
    return await Api().get("/configs/active");
  }
}

export default new ConfigService();
