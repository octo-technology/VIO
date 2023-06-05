<template>
  <div class="container">
    <div v-if="itemId !== null">
      <p>Item id: {{ itemId }}</p>
      <p class="decision">{{ decision }}</p>
      <div v-for="(object, index) in predictedItem" :key="index">
        <div class="inference-image">
          <div
            v-for="(inference, model_id) in object.inferences"
            :key="model_id"
          >
            <div v-if="inference !== 'NO_DECISION'">
              <div v-for="(result, object_id) in inference" :key="object_id">
                <div v-if="'location' in result">
                  <Box
                    v-if="imgLoaded"
                    v-bind:x-min="result['location'][0] * width"
                    v-bind:y-min="result['location'][1] * height"
                    v-bind:x-max="result['location'][2] * width"
                    v-bind:y-max="result['location'][3] * height"
                  />
                </div>
              </div>
            </div>
          </div>
          <img
            class="img-responsive"
            ref="image"
            :src="object.image_url"
            @load="on_image_loaded"
          />
        </div>
      </div>
    </div>

    <div v-if="doneStatus" class="no_configuration">
      <v-alert color="green" dismissible elevation="10" type="success"
        >{{ this.doneStatus }}
      </v-alert>
    </div>
  </div>
</template>

<script>
import Box from "./Box";

export default {
  name: "inference",
  components: { Box },
  props: [
    "predictedItem",
    "itemId",
    "statusList",
    "state",
    "decision",
    "doneStatus"
  ],
  data: () => ({
    imgLoaded: false,
    height: null,
    width: null
  }),
  methods: {
    on_image_loaded() {
      let img = this.$refs.image[0];
      this.height = img.height;
      this.width = img.width;
      console.log("Image size : ", this.height, this.width);
      this.imgLoaded = true;
    },
    getColor(status) {
      if (this.statusList[status] > this.statusList[this.state]) {
        return "red";
      } else {
        return "green";
      }
    }
  }
};
</script>

<style lang="scss" scoped>
.inference-image {
  display: inline-block;
  position: relative;
}

.container {
  text-align: center;
}

.decision {
  font-weight: bold;
  font-size: 3rem;
}

.timeline {
  padding: 1rem;
  overflow-x: hidden;
}

.img-responsive {
  max-width: 400px;
  width: 100%;
  height: auto;
}

ol {
  margin-bottom: 5px;
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
