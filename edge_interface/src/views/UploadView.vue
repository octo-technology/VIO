<template>
  <v-col class="container" cols="12">
    <v-row>
      <div class="col-md-6">
        <div>
          <h2 v-if="isStart">Current Camera</h2>
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
        </div>

        <div class="row">
          <div v-if="isStart" class="col-md-12">
            <v-select
              v-model="camera"
              v-if="devices.length > 2"
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
            <v-btn
              v-if="devices.length == 2"
              color="blue-grey"
              class="mr-4 white--text"
              @click="onSwitchCamera"
            >
              <v-icon dark>mdi-swap-vertical</v-icon>
            </v-btn>
            <v-btn v-if="isStart" color="error" class="mr-4" @click="onCapture">
              Capture Photo
            </v-btn>
            <v-btn v-if="isStart" color="error" class="mr-4" @click="onStop">
              Stop Camera
            </v-btn>
            <v-btn v-if="!isStart" color="error" class="mr-4" @click="onStart">
              Start Camera
            </v-btn>
          </div>
        </div>
      </div>
      <div v-if="img" class="col-md-6">
        <h2>Captured Image</h2>
        <figure class="figure">
          <img :src="img" class="img-responsive" />
        </figure>

        <div class="row">
          <div class="col-md-12">
            <UploadImage
              :errorMessage="errorMessage"
              :doneStatus="doneStatus"
              :image="this.img"
              @update-error-message="updateErrorMessage"
              @update-done-status="updatedoneStatus"
            />
            <Inference
              :errorMessage="errorMessage"
              :image="this.img"
              @update-error-message="updateErrorMessage"
            />
            <div v-if="errorMessage !== null" class="no_configuration">
              <v-alert color="red" dismissible elevation="10" type="warning"
                >{{ this.errorMessage }}
              </v-alert>
            </div>
            <div v-if="doneStatus !== null" class="no_configuration">
              <v-alert color="green" dismissible elevation="10" type="success"
                >{{ this.doneStatus }}
              </v-alert>
            </div>
          </div>
        </div>
      </div>
    </v-row>
  </v-col>
</template>

<script>
import VideoCapture from "@/components/VideoCapture";
import Inference from "@/components/Inference";
import UploadImage from "@/components/UploadImage";

export default {
  name: "UploadView",
  data: () => ({
    img: null,
    camera: null,
    deviceId: null,
    errorMessage: null,
    doneStatus: null,
    devices: [],
    isStart: true
  }),
  components: {
    UploadImage,
    VideoCapture,
    Inference
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
    },
    doneStatus: function(newVal) {
      if (newVal) {
        setTimeout(() => {
          this.doneStatus = null;
        }, 5000);
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
      this.isStart = false;
      this.$refs.webcam.stop();
    },
    onStart() {
      this.isStart = true;
      this.$refs.webcam.start();
    },
    checkDeviceId(device) {
      return device.deviceId == this.deviceId;
    },
    onSwitchCamera() {
      const newIndex = 1 - this.devices.findIndex(this.checkDeviceId);
      const newDeviceId = this.devices[newIndex].deviceId;
      this.deviceId = newDeviceId;
      this.camera = newDeviceId;
      console.log("On Camera Change Event", this.deviceId);
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
    },
    updateErrorMessage(errorMessage) {
      this.errorMessage = errorMessage;
    },
    updatedoneStatus(doneStatus) {
      this.doneStatus = doneStatus;
    }
  }
};
</script>

<style lang="scss" scoped>
.container {
  text-align: center;
}

.red {
  background: #d41928;
}

.green {
  background: #51d419;
}

.img-responsive {
  max-width: 400px;
  width: 100%;
  height: auto;
}
</style>
