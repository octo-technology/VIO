import Api from '@/services/api'

class UploadFilesService {
  upload(inputs, sensors, binaries) {
    const formData = new FormData()
    formData.append('inputs', inputs)
    formData.append('sensors', sensors)
    // formData.append("binaries", binaries);

    for (let i = 0; i < binaries.length; i++) {
      formData.append('binaries', binaries[i])
    }

    for (const value of formData.values()) {
      console.log(value)
    }

    return Api().put('/items', formData)
  }
}

export default new UploadFilesService()
