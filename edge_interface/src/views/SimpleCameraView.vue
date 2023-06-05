<template>
    <v-col class="container">
        <div>
            <video-capture ref="webcam" :device-id="deviceId" @started="onStarted" @stopped="onStopped" @error="onError"
                @cameras="onCameras" @camera-change="onCameraChange">
            </video-capture>

            <v-fab-transition>
                <v-btn color="blue darken-3" dark absolute bottom right fab @click="trigger" style="bottom: 16px">
                    <v-icon>mdi-camera-outline</v-icon>
                </v-btn>
            </v-fab-transition>
        </div>



        <div v-if="errorMessage" class="no_configuration">
            <v-alert color="red" dismissible elevation="10" type="warning">{{ this.errorMessage }}
            </v-alert>
        </div>

    </v-col>
</template>

<script>
import VideoCapture from "@/views/components/VideoCapture";
import UploadService from "@/services/UploadCameraService";
import TriggerCaptureService from "@/services/TriggerCaptureService";

export default {
    name: "SimpleCameraView",
    data: () => ({
        camera: null,
        devices: [],
        deviceId: null,
        errorMessage: null,
        loading: false,
    }),
    components: {
        VideoCapture
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
            // console.log(first);
            if (first) {
                this.camera = first.deviceId;
                this.deviceId = first.deviceId;
            }
        }
    },
    methods: {
        onStarted(stream) { 
            // console.log("On Started Event", stream); 
        },
        onStopped(stream) { 
            console.log("On Stopped Event", stream); 
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
        async trigger() {
            const image = this.$refs.webcam.capture();

            var trigger = (image != undefined)
                ? UploadService.inference(image)
                : TriggerCaptureService.trigger();

            trigger
                .then(async (response) => {
                    let itemId = response.data["item_id"];
                    // console.log("Returned ID", itemId)
                    this.$router.push({ name: "Simple-Result", params: { itemId: itemId } });

                })
                .catch((reason) => {
                    if (reason == "Error: Network Error") {
                        this.updateErrorMessage(reason);
                    } else if (reason.response.status === 403) {
                        // console.log(reason.response.data);
                        this.updateErrorMessage(reason.response.data["message"]);
                        this.itemId = null;
                    } else {
                        // console.log(reason.response.data);
                    }
                    this.loading = false;
                });
        }
    }
}
</script>

<style lang="scss" scoped>
.container {
    text-align: center;
    margin: 0;
    padding: 0;
}
</style>