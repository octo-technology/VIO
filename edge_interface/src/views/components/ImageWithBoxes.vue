<template>
    <div class="inference-image">
        <div v-for="(inference, model_id) in camera.inferences" :key="model_id">
            <div v-if="inference !== 'NO_DECISION'">
                <div v-for="(result, box_id) in inference" :key="box_id">
                    <div v-if="'location' in result">
                        <Box v-if="imgLoaded" :identity="{ camera: camera.camera_id, model: model_id, box: box_id }"
                            :x-min="result['location'][0] * width" :y-min="result['location'][1] * height"
                            :x-max="result['location'][2] * width" :y-max="result['location'][3] * height" />
                    </div>
                </div>
                <div v-for="box, index in additional_boxes" :key="index">
                    <Box v-if="imgLoaded" :x-min="box['location'][0] * width" :y-min="box['location'][1] * height"
                        :x-max="box['location'][2] * width" :y-max="box['location'][3] * height" />
                </div>
            </div>
        </div>
        <img class="img-responsive" ref="image" :src="camera.image_url" @load="on_image_loaded" @click="onClickImage" />
    </div>
</template>

<script>
import Box from "./Box";

export default {
    data: () => ({
        imgLoaded: false,
        height: null,
        width: null,
        additional_boxes: [],
        forcedWidth: 500,
    }),
    components: {
        Box
    },
    props: {
        camera: {}
    },
    mounted() {
        // console.log("mounted", this.camera)
    },
    methods: {
        on_image_loaded() {
            let img = this.$refs.image;
            this.height = img.height
            this.width = img.width;
            this.imgLoaded = true;
        },
        onClickImage(event) {

            let x = event.offsetX / this.width
            let y = event.offsetY / this.height
            let width = 0.1
            let height = 0.1

            // this.additional_boxes.push({
            //     type: 'manual',
            //     location: [
            //         x - width / 2,
            //         y - height / 2,
            //         x + width / 2,
            //         y + height / 2
            //     ]
            // })
        },
    }
}
</script>

<style lang="scss" scoped>
.img-responsive {
    max-height: 400px;
    width: 100%;
    height: auto;
}

.inference-image {
    display: inline-block;
    position: relative;
}
</style>