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

class UploadCameraService {
  upload(image) {
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

export default new UploadCameraService();
