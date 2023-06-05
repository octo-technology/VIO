<template>
    <v-col class="container">
        <div v-if="!img">
            <div class="border">
                <video-capture ref="webcam" :device-id="deviceId" width="100%" @started="onStarted" @stopped="onStopped"
                    @error="onError" @cameras="onCameras" @camera-change="onCameraChange" />
            </div>

            <div>
                <div v-if="isStart">
                    <v-select v-if="devices.length > 2" v-model="camera" :items="devices" item-text="label"
                        item-value="deviceId" label="Camera" required>
                    </v-select>

                    <code v-if="device">{{ device.label }}</code>
                </div>

                <div class="col-md-12">
                    <v-btn v-if="devices.length == 2" color="blue-grey" class="mr-4 white--text" @click="onSwitchCamera">
                        <v-icon dark>mdi-swap-vertical</v-icon>
                    </v-btn>
                </div>
            </div>
        </div>

        <div>
            <v-fab-transition>
                <v-btn v-show="!isTrigger" color="blue darken-3" dark absolute bottom right fab style="bottom: 16px"
                    @click="trigger">
                    <v-icon>mdi-camera-outline</v-icon>
                </v-btn>
            </v-fab-transition>

            <v-fab-transition>
                <v-btn v-show="isTrigger" color="blue darken-3" dark absolute bottom right fab style="bottom: 16px"
                    @click="backCamera">
                    <v-icon>mdi-arrow-left</v-icon>
                </v-btn>
            </v-fab-transition>

            <div class="row">
                <div class="col-md-12">
                    <Inference v-if="this.img" :predictedItem="predictedItem" :itemId="itemId" :statusList="statusList"
                        :state="state" :decision="decision" :doneStatus="doneStatus" />
                    <v-progress-circular v-if="loading" indeterminate color="blue darken-3"></v-progress-circular>
                    <div v-if="errorMessage" class="no_configuration">
                        <v-alert color="red" dismissible elevation="10" type="warning">{{ this.errorMessage }}
                        </v-alert>
                    </div>
                </div>
            </div>
        </div>
    </v-col>
</template>

<script>
import VideoCapture from "@/views/components/VideoCapture";
import Inference from "@/views/components/Inference";

import ItemsService from "@/services/ItemsService";
import UploadService from "@/services/UploadCameraService";
import TriggerCaptureService from "@/services/TriggerCaptureService";
import { baseURL } from "@/services/api";

export default {
    name: "UploadView",
    data: () => ({
        img: null,
        camera: null,
        deviceId: null,
        errorMessage: null,
        doneStatus: null,
        devices: [],
        isStart: true,

        loading: false,
        isTrigger: false,
        predictedItem: {},
        itemId: null,
        statusList: null,
        state: undefined,
        decision: undefined,
    }),
    components: {
        VideoCapture,
        Inference,
    },

    computed: {
        device: function () {
            return this.devices.find((n) => n.deviceId === this.deviceId);
        },
    },
    watch: {
        camera: function (id) {
            this.deviceId = id;
        },
        devices: function () {
            var first;
            if (this.devices.length >= 2) first = this.devices[1];
            else first = this.devices[0];
            console.log(first);
            if (first) {
                this.camera = first.deviceId;
                this.deviceId = first.deviceId;
            }
        },
        doneStatus: function (newVal) {
            if (newVal) {
                setTimeout(() => {
                    this.doneStatus = null;
                }, 5000);
            }
        },
        errorMessage: function (newVal) {
            if (newVal) {
                setTimeout(() => {
                    this.errorMessage = null;
                }, 5000);
            }
        },
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
            console.log("On switch camera Event", this.deviceId);
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
        },
        backCamera() {
            this.isTrigger = false;
            this.img = null;
            // this.onStart()
        },
        async waitForStateDone() {
            const maxAttempts = 20;
            let attempts = 0;
            this.statusList = {
                Capture: 0,
                "Save Binaries": 1,
                Inference: 2,
                Decision: 3,
                Done: 4,
            };
            const executePoll = async (resolve, reject) => {
                const result = await ItemsService.get_item_state_by_id(this.itemId);
                this.state = result.data;
                console.log("STATE POLLING", this.state);
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
            this.loading = true;
            const image = this.$refs.webcam.capture();
            this.predictedItem = [];

            if (image != undefined) var trigger = UploadService.inference(image);
            else trigger = TriggerCaptureService.trigger();

            trigger
                .then(async (response) => {
                    this.itemId = response.data["item_id"];
                    console.log("Returned ID", response.data["item_id"])
                    this.updateErrorMessage(null);

                    await this.waitForStateDone();
                    const itemResponse = await ItemsService.get_item_by_id(this.itemId);
                    const item = itemResponse.data;
                    console.log(item);
                    this.decision = item["decision"];
                    const inferences = item["inferences"];
                    Object.keys(inferences).forEach((camera_id) => {
                        this.predictedItem.push({
                            camera_id: camera_id,
                            inferences: inferences[camera_id],
                            image_url: `${baseURL}/items/${this.itemId}/binaries/${camera_id}`,
                        });
                    });
                    this.updatedoneStatus("Inference finished");
                    console.log(this.predictedItem);
                    this.isTrigger = true;
                    this.img = image;
                    this.onStop();
                    this.loading = false;
                    // this.devices = [];
                    // console.log(this.devices)
                    // console.log(this.camera)
                    this.deviceId = null;
                })
                .catch((reason) => {
                    if (reason == "Error: Network Error") {
                        this.updateErrorMessage(reason);
                    } else if (reason.response.status === 403) {
                        console.log(reason.response.data);
                        this.updateErrorMessage(reason.response.data["message"]);
                        this.itemId = null;
                    } else {
                        console.log(reason.response.data);
                    }
                    this.loading = false;
                });
        },
    },
};
</script>

<style lang="scss" scoped>
.container {
    text-align: center;
    //background-color: black;
    height: 100vh;
}

.red {
    background: #d41928;
}

.green {
    background: #51d419;
}
</style>
