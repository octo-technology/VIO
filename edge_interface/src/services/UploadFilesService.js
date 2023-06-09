import Api from '@/services/api.js'

class UploadFilesService {
  upload(inputs, sensors, binaries) { // eslint-disable-line
    const formData = new FormData()
    formData.append('inputs', inputs)
    formData.append('sensors', sensors)

    for (let i = 0; i < binaries.length; i++) { // eslint-disable-line
      formData.append('binaries', binaries[i])
    }
    return Api().put('/items', formData)
  }
}

export default new UploadFilesService()
