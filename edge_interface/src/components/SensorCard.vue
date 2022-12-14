<template>
  <v-card tile>
    <v-card-title class="img-title mb-0 pb-0">
      <img
        ref="card_image"
        :src="urlBinary"
        width="100%"
        @load="on_image_loaded"
      />
      <canvas ref="card_canvas" v-bind:class="{ loaded: isImageLoaded }">
      </canvas>
    </v-card-title>

    <v-list-item>
      <v-list-item-content>
        <v-list-item-title class="headline mb-1">{{
          sensor_id
        }}</v-list-item-title>
      </v-list-item-content>

      <div v-show="has_decision">
        <v-list-item-avatar
          tile
          size="40"
          :color="getDecisionState === 'OK' ? 'green' : 'red'"
          class="mr-0"
          >{{ getDecisionState }}
        </v-list-item-avatar>
      </div>
    </v-list-item>

    <div v-show="has_decision">
      <v-alert
        tile
        type="error"
        text
        v-for="(errors, index) in getErrors"
        :key="index"
        border="right"
        colored-border
      >
        {{ errors }}
      </v-alert>
    </div>
    <v-card-actions>
      <v-btn @click="zoom_on_card" text>
        Zoom
      </v-btn>
      <v-spacer></v-spacer>
      <v-btn icon @click="show = !show">
        <v-icon>{{ show ? "mdi-chevron-up" : "mdi-chevron-down" }}</v-icon>
      </v-btn>
    </v-card-actions>

    <v-expand-transition>
      <div v-show="show">
        <v-divider></v-divider>
        <v-card-text class="text--primary">
          <ul>
            <li>Decision: {{ getDecision }}</li>
            <li>Binary filename: {{ getSensor.binary_filename }}</li>
            <li>Metadata:</li>
            <div>{{ getSensor.metadata }}</div>
            <li>Inference:</li>
            <div>{{ getInference }}</div>
          </ul>
        </v-card-text>
      </div>
    </v-expand-transition>
  </v-card>
</template>

<script>
import { getUrlBinary } from "@/services/methods";

export default {
  name: "sensorcard",
  data: function() {
    return {
      isImageLoaded: false,
      show: false
    };
  },

  props: {
    item: {
      type: Object,
      required: true
    },
    sensor_id: {
      type: String,
      required: true
    }
  },

  computed: {
    urlBinary() {
      const binaryName = this.item.sensors[this.sensor_id].binary_filename;
      return getUrlBinary(this.item._id, binaryName);
    },
    getSensor() {
      if (this.item.sensors == null) {
        return "Fail to get sensors";
      } else {
        return this.item.sensors[this.sensor_id];
      }
    },
    getInference() {
      if (this.item.inferences == null) {
        return "Fail to get inferences";
      } else {
        return this.item.inferences[this.sensor_id];
      }
    },
    getDecision() {
      if (this.item.decision == null) {
        return "Fail to get decision";
      } else {
        return this.item.decision[this.sensor_id];
      }
    },

    getDecisionState() {
      let decision = this.getDecision;
      if (decision === "Fail to get decision") return "";
      else return decision.decision.result;
    },
    getErrors() {
      let decision = this.getDecision;
      if (decision === "Fail to get decision") return "";
      else return decision.decision.errors;
    },
    has_decision() {
      let decision = this.getDecision;
      if (decision === "Fail to get decision") return false;
      else return true;
    }
  },

  methods: {
    on_image_loaded(/*event*/) {
      // build canvas
      let canvas = this.$refs.card_canvas;
      let img = this.$refs.card_image;

      let context = canvas.getContext("2d");
      let width = img.width;
      let height = img.height;
      context.canvas.width = width;
      context.canvas.height = height;
      context.clearRect(0, 0, img.width, img.height);

      let inferences = this.getInference;
      if (inferences === "Fail to get inferences") return;
      for (const [model_name, inference] of Object.entries(inferences)) {
        console.log(model_name, inference);
        if (inference.model.category == "object_detection") {
          console.log("object detection !!");
          context.beginPath();
          for (const [object_id, properties] of Object.entries(
            inference.output
          )) {
            console.debug(object_id);
            let location = properties.location;
            let x = location[0] * width;
            let y = location[1] * height;
            let w = (location[2] - location[0]) * width;
            let h = (location[3] - location[1]) * height;
            context.rect(x, y, w, h);
          }
          context.stroke();
        }
      }
      this.isImageLoaded = true;
    },

    zoom_on_card(/*event*/) {
      alert("Not Implemented");
    }
  }
};
</script>

<style lang="scss" scoped>
canvas.loaded {
  position: absolute;
  display: block;
}

canvas {
  display: none;
}

.img-title {
  padding: 0 0 16px 0;
}
</style>
