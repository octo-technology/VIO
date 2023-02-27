import Api from "@/services/api";

const b64toBlob = (b64Data, contentType = "", sliceSize = 512) => {
  const byteCharacters = atob(b64Data);
  const byteArrays = [];

  for (let offset = 0; offset < byteCharacters.length; offset += sliceSize) {
    const slice = byteCharacters.slice(offset, offset + sliceSize);

    const byteNumbers = new Array(slice.length);
    for (let i = 0; i < slice.length; i++) {
      byteNumbers[i] = slice.charCodeAt(i);
    }

    const byteArray = new Uint8Array(byteNumbers);
    byteArrays.push(byteArray);
  }

  return new Blob(byteArrays, { type: contentType });
};

class UploadFilesService {
  upload(inputs, sensors, binaries) {
    let formData = new FormData();
    formData.append("inputs", inputs);
    formData.append("sensors", sensors);
    //formData.append("binaries", binaries);

    for (let i = 0; i < binaries.length; i++) {
      formData.append("binaries", binaries[i]);
    }

    for (let value of formData.values()) {
      console.log(value);
    }

    return Api().put("/items", formData);
  }

  uploadImage(image) {
    const splitComma = image.split(",");
    const base64 = splitComma[1];
    const contentType = splitComma[0].split(":")[1].split(";")[0];
    const blob = b64toBlob(base64, contentType);
    let formData = new FormData();

    formData.append("image", blob, contentType);
    return Api().post("/upload", formData, {
      headers: {
        "content-Type": "multipart/form-data"
      }
    });
  }
}

export default new UploadFilesService();
