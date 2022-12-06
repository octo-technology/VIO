<template>
  <v-col cols="12">
    <v-row>
      <h2>Current Camera</h2>
      <div>
        <div class="border">
          <video-capture
            ref="webcam"
            :device-id="deviceId"
            width="100%"
            @started="onStarted"
            @stopped="onStopped"
            @error="onError"
            @cameras="onCameras"
            @camera-change="onCameraChange"
          />
        </div>

        <div class="row">
          <div class="col-md-12">
            <v-select
              v-model="camera"
              :items="devices"
              item-text="label"
              item-value="deviceId"
              label="Camera"
              required
            >
            </v-select>

            <code v-if="device">{{ device.label }}</code>
          </div>
          <div class="col-md-12">
            <v-btn color="error" class="mr-4" @click="onCapture">
              Capture Photo</v-btn
            >
            <v-btn color="error" class="mr-4" @click="onStop">
              Stop Camera
            </v-btn>
            <v-btn color="error" class="mr-4" @click="onStart">
              Start Camera
            </v-btn>
          </div>
        </div>
      </div>
      <div class="col-md-6">
        <h2>Captured Image</h2>
        <figure class="figure">
          <img :src="img" class="img-responsive" />
        </figure>
      </div>
    </v-row>
  </v-col>
</template>

<script>
import VideoCapture from "../components/VideoCapture.vue";

export default {
  name: "UploadView",
  data: () => ({
    img: null,
    camera: null,
    deviceId: null,
    devices: []
  }),
  components: {
    VideoCapture
  },

  computed: {
    device: function() {
      return this.devices.find(n => n.deviceId === this.deviceId);
    }
  },
  watch: {
    camera: function(id) {
      this.deviceId = id;
    },
    devices: function() {
      // Once we have a list select the first one
      const first = this.devices[0];
      if (first) {
        this.camera = first.deviceId;
        this.deviceId = first.deviceId;
      }
    }
  },
  methods: {
    onCapture() {
      this.img = this.$refs.webcam.capture();
    },
    onStarted(stream) {
      console.log("On Started Event", stream);
    },
    onStopped(stream) {
      console.log("On Stopped Event", stream);
    },
    onStop() {
      this.$refs.webcam.stop();
    },
    onStart() {
      this.$refs.webcam.start();
    },
    onError(error) {
      console.log("On Error Event", error);
    },
    onCameras(cameras) {
      this.devices = cameras;
      console.log("On Cameras Event", cameras);
    },
    onCameraChange(deviceId) {
      this.deviceId = deviceId;
      this.camera = deviceId;
      console.log("On Camera Change Event", deviceId);
    }
  }
};
</script>
