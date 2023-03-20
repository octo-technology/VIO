import Api from "@/services/api";

class ItemsService {
  async get_items() {
    return await Api().get("/items");
  }

  async get_item_by_id(id) {
    return await Api().get(`/items/${id}`);
  }

  async get_item_state_by_id(id) {
    return await Api().get(`/items/${id}/state`);
  }

  async getItemBinaryForCameraById(id, camera_id) {
    return await Api().get(`/items/${id}/binaries/${camera_id}`, {
      responseType: "arraybuffer"
    });
  }
}

export default new ItemsService();
