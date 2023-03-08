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
            <v-btn color="error" class="mr-4" @click="onCapture">
              Capture Photo</v-btn
            >
            <v-btn color="blue-grey" class="mr-4 white--text" @click="trigger">
              Trigger
              <v-icon right dark>mdi-cloud-upload</v-icon>
            </v-btn>
            <v-btn color="error" class="mr-4" @click="upload"> Upload</v-btn>
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
        :item_id="item_id"
        :errorMessage="errorMessage"
        :decision="decision"
      />

      <div v-if="errorMessage !== null" class="no_configuration">
        <v-alert color="red" dismissible elevation="10" type="warning"
          >{{ this.errorMessage }}
        </v-alert>
      </div>
      <div v-if="done_status !== null" class="no_configuration">
        <v-alert color="green" dismissible elevation="10" type="success"
          >{{ this.done_status }}
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
    item_id: null,
    errorMessage: null,
    done_status: null,
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
    done_status: function(new_val) {
      if (new_val) {
        setTimeout(() => {
          this.done_status = null;
        }, 3000);
      }
    }
  },
  methods: {
    onCapture() {
      this.img = this.$refs.webcam.capture();
    },
    async upload() {
      await UploadService.upload(this.$refs.webcam.capture())
        .then(async response => {
          this.item_id = response.data["item_id"];
          this.errorMessage = null;
          this.done_status = "Image upload trigger";
        })
        .catch(reason => {
          if (reason.response.status === 403) {
            console.log(reason.response.data);
            this.errorMessage = reason.response.data["message"];
            this.item_id = null;
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
        const result = await ItemsService.get_item_state_by_id(this.item_id);
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
          this.item_id = response.data["item_id"];
          this.errorMessage = null;

          await this.waitForStateDone();
          const itemResponse = await ItemsService.get_item_by_id(this.item_id);
          const item = itemResponse.data;
          this.decision = item["decision"];
          const inferences = item["inferences"];
          Object.keys(inferences).forEach(camera_id => {
            this.predictedItem.push({
              camera_id: camera_id,
              inferences: inferences[camera_id],
              image_url: `${baseURL}/items/${this.item_id}/binaries/${camera_id}`
            });
          });
        })
        .catch(reason => {
          if (reason.response.status === 403) {
            console.log(reason.response.data);
            this.errorMessage = reason.response.data["message"];
            this.item_id = null;
          } else {
            console.log(reason.response.data);
          }
        });
    },
    getColor(status) {
      if (this.statusList[status] > this.statusList[this.state]) {
        return "red";
      } else {
        return "green";
      }
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

.result {
  display: inline-block;
  vertical-align: top;
  padding: 0 5rem 0 5rem;
}

.decision {
  font-weight: bold;
  font-size: 3rem;
}

.box {
  position: absolute;
  border: 2px #f30b0b solid;
}

#image-wrapper {
  background-repeat: no-repeat;
  position: relative;
}

.no_configuration {
  padding: 6rem 0;
}

.timeline {
  padding: 3rem;
  white-space: nowrap;
  overflow-x: hidden;
}

ol {
  display: inline-block;
  list-style: none;
}

.timeline ol li {
  position: relative;
  display: inline-block;
  list-style-type: none;
  width: 160px;
  height: 3px;
  background: #bfbfbf;
}

.line {
  content: "";
  position: absolute;
  top: 50%;
  left: calc(100% + 1px);
  bottom: 0;
  width: 12px;
  height: 12px;
  transform: translateY(-50%);
  border-radius: 50%;
}

.red {
  background: #d41928;
}

.green {
  background: #51d419;
}
</style>
