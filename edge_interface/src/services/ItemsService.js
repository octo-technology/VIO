import Api from '@/services/api.js'

class ItemsService {
  async getItems() {
    const items = await Api().get('/items')
    return items
  }

  async getItemById(id) {
    const itemsById = await Api().get(`/items/${id}`)
    return itemsById
  }

  async getItemStateById(id) {
    const itemsResponse = await Api().get(`/items/${id}/state`)
    return itemsResponse
  }

  async getItemBinaryForCameraById(id, cameraId) {
    const itemBynaryForCamera = await Api().get(`/items/${id}/binaries/${cameraId}`, {
      responseType: 'arraybuffer'
    })
    return itemBynaryForCamera
  }
}

export default new ItemsService()
