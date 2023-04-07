<template>
  <div class="container">
    <div class="UploadView__capture-content">
    <h2>Use a photo to evaluate model inference</h2>
    <div class="UploadView__image-content">
      <video-capture
        v-show="!isAnyImageCaptured"
        ref="webcam"
        :device-id="deviceId"
        width="100%"
        height="100%"
        @cameras="getCameraDevices"
        @camera-change="onCameraDeviceChange"
      />
      <img
        v-if="isAnyImageCaptured"
        :src="imagePath"
        class="UploadView__img-captured" />
    </div>
    <v-btn color="black" :icon=true fab large @click="onCaptureImage">
      <v-icon>mdi-camera</v-icon>
    </v-btn>
  </div>
  <v-btn color="grey" class="mr-4" :disabled="!isAnyImageCaptured">
    <span> > Inference</span>
  </v-btn>
  </div>
</template>

<script>
import VideoCapture from "@/components/VideoCapture";
import { mapGetters } from 'vuex'

export default {
  name: "VUploadView",
  data: () => ({
    deviceId: null,
    devices: [],
  }),
  components: {
    VideoCapture
  },

  computed: {
    device() {
      return this.devices.find(device => device.deviceId === this.deviceId);
    },
    isAnyImageCaptured() {
      return this.imagePath != null;
    },
    ...mapGetters(['imagePath'])
  },
  watch: {
    deviceId: function(id) {
      this.deviceId = id;
    },
    devices: function() {
      // Once we have a list select the first one
      const first = this.devices[0];
      if (first) {
        this.deviceId = first.deviceId;
      }
    }
  },
  methods: {
    getCameraDevices(devices) {
      this.devices = devices;
    },
    onCameraDeviceChange(deviceId) {
      this.deviceId = deviceId;
    },
    onCaptureImage() {
      let imagePathToCommit = this.imagePath != null ? null : this.captureImage()
      this.$store.commit("SET_IMAGE_PATH", imagePathToCommit)
    },
    captureImage() {
      return this.$refs.webcam.capture()
    }
  }
};
</script>

<style lang="scss" scoped>
.container {
  text-align: center;
}
.UploadView__image-content {
  max-width: 60%;
  width: 100%;
  margin: auto;
}
.UploadView__capture-content {
  padding: 50px 0;
}
.UploadView__img-captured {
  width: 100%;
}
</style>
