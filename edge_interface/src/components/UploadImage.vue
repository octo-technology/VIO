<template>
  <v-btn color="error" class="mr-4" @click="upload">Upload</v-btn>
</template>
<script>
import UploadService from "@/services/UploadCameraService";

export default {
  name: "UploadImage",
  props: ["errorMessage", "doneStatus", "image"],
  methods: {
    async upload() {
      await UploadService.upload(this.image)
        .then(() => {
          this.$emit("update-error-message", null);
          this.$emit("update-done-status", "Image upload trigger");
        })
        .catch(reason => {
          if (reason.response.status === 403) {
            console.log(reason.response.data);
            this.$emit("update-error-message", reason.response.data["message"]);
          } else {
            console.log(reason.response.data);
          }
        });
    }
  }
};
</script>
