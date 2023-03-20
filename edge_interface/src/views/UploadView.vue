<template>
  <v-col class="container" cols="12">
    <v-row>
      <div class="col-md-6">
        <h2>Current Camera</h2>
      </div>
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
            <v-btn color="blue-grey" class="mr-4 white--text" @click="trigger">
              Trigger
              <v-icon right dark>mdi-cloud-upload</v-icon>
            </v-btn>
            <v-btn color="error" class="mr-4" @click="upload">Upload</v-btn>
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

      <Inference
        :predictedItem="predictedItem"
        :statusList="statusList"
        :state="state"
        :itemId="itemId"
        :errorMessage="errorMessage"
        :decision="decision"
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
    </v-row>
  </v-col>
</template>

<script>
import UploadService from "@/services/UploadCameraService";
import VideoCapture from "@/components/VideoCapture.vue";
import Inference from "@/components/Inference";
import ItemsService from "@/services/ItemsService";
import { baseURL } from "@/services/api";

export default {
  name: "UploadView",
  data: () => ({
    img: null,
    camera: null,
    deviceId: null,
    itemId: null,
    errorMessage: null,
    doneStatus: null,
    devices: [],

    predictedItem: {},
    state: undefined,
    decision: undefined,
    statusList: null
  }),
  components: {
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
        }, 3000);
      }
    }
  },
  methods: {
    async upload() {
      await UploadService.upload(this.$refs.webcam.capture())
        .then(async response => {
          this.itemId = response.data["item_id"];
          this.errorMessage = null;
          this.doneStatus = "Image upload trigger";
        })
        .catch(reason => {
          if (reason.response.status === 403) {
            console.log(reason.response.data);
            this.errorMessage = reason.response.data["message"];
            this.itemId = null;
          } else {
            console.log(reason.response.data);
          }
        });
    },

    async waitForStateDone() {
      const maxAttempts = 20;
      let attempts = 0;
      this.statusList = {
        Capture: 0,
        "Save Binaries": 1,
        Inference: 2,
        Decision: 3,
        Done: 4
      };
      const executePoll = async (resolve, reject) => {
        const result = await ItemsService.get_item_state_by_id(this.itemId);
        this.state = result.data;
        attempts++;

        if (this.state === "Done") {
          return resolve(result);
        } else if (attempts === maxAttempts) {
          return reject(new Error("L'inférence n'a pas pu être réalisée"));
        } else {
          setTimeout(executePoll, 800, resolve, reject);
        }
      };

      return new Promise(executePoll);
    },
    async trigger() {
      this.predictedItem = [];
      await UploadService.inference(this.$refs.webcam.capture())
        .then(async response => {
          this.itemId = response.data["item_id"];
          this.errorMessage = null;

          await this.waitForStateDone();
          const itemResponse = await ItemsService.get_item_by_id(this.itemId);
          const item = itemResponse.data;
          this.decision = item["decision"];
          const inferences = item["inferences"];
          Object.keys(inferences).forEach(camera_id => {
            this.predictedItem.push({
              camera_id: camera_id,
              inferences: inferences[camera_id],
              image_url: `${baseURL}/items/${this.itemId}/binaries/${camera_id}`
            });
          });
        })
        .catch(reason => {
          if (reason.response.status === 403) {
            console.log(reason.response.data);
            this.errorMessage = reason.response.data["message"];
            this.itemId = null;
          } else {
            console.log(reason.response.data);
          }
        });
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

<style lang="scss" scoped>
.container {
  text-align: center;
}

.no_configuration {
  padding: 6rem 0;
}

.red {
  background: #d41928;
}

.green {
  background: #51d419;
}
</style>
