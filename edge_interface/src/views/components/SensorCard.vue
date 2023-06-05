<template>
  <v-card tile>
    <v-card-title class="img-title mb-0 pb-0">
      <img ref="card_image" :src="urlBinary" width="100%" @load="on_image_loaded" />
      <canvas ref="card_canvas" :class="{ loaded: isImageLoaded }" />
    </v-card-title>

    <v-list-item>
      <v-list-item-content>
        <v-list-item-title class="headline mb-1">
          {{ sensor_id }}
        </v-list-item-title>
      </v-list-item-content>

      <div v-show="has_decision">
        <v-list-item-avatar tile size="40" :color="getDecisionState === 'OK' ? 'green' : 'red'" class="mr-0">
          {{ getDecisionState }}
        </v-list-item-avatar>
      </div>
    </v-list-item>

    <div v-show="has_decision">
      <v-alert v-for="(errors, index) in getErrors" :key="index" tile type="error" text border="right" colored-border>
        {{ errors }}
      </v-alert>
    </div>
    <v-card-actions>
      <v-btn text @click="zoom_on_card">
        Zoom
      </v-btn>
      <v-spacer />
      <v-btn icon @click="show = !show">
        <v-icon>{{ show ? 'mdi-chevron-up' : 'mdi-chevron-down' }}</v-icon>
      </v-btn>
    </v-card-actions>

    <v-expand-transition>
      <div v-show="show">
        <v-divider />
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
import { getUrlBinary } from '@/services/methods'

export default {
  name: 'Sensorcard',

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
  data() {
    return {
      isImageLoaded: false,
      show: false
    }
  },

  computed: {
    urlBinary() {
      const binaryName = this.item.sensors[this.sensor_id].binary_filename
      return getUrlBinary(this.item.id, binaryName)
    },
    getSensor() {
      if (this.item.sensors == null) {
        return 'Fail to get sensors'
      }
      return this.item.sensors[this.sensor_id]
    },
    getInference() {
      if (this.item.inferences == null) {
        return 'Fail to get inferences'
      }
      return this.item.inferences[this.sensor_id]
    },
    getDecision() {
      if (this.item.decision == null) {
        return 'Fail to get decision'
      }
      return this.item.decision[this.sensor_id]
    },

    getDecisionState() {
      const decision = this.getDecision
      if (decision === 'Fail to get decision') return ''
      return decision.decision.result
    },
    getErrors() {
      const decision = this.getDecision
      if (decision === 'Fail to get decision') return ''
      return decision.decision.errors
    },
    has_decision() {
      const decision = this.getDecision
      if (decision === 'Fail to get decision') return false
      return true
    }
  },

  methods: {
    on_image_loaded(/* event */) {
      // build canvas
      const canvas = this.$refs.card_canvas
      const img = this.$refs.card_image

      const context = canvas.getContext('2d')
      const { width } = img
      const { height } = img
      context.canvas.width = width
      context.canvas.height = height
      context.clearRect(0, 0, img.width, img.height)

      const inferences = this.getInference
      if (inferences === 'Fail to get inferences') return
      for (const [model_name, inference] of Object.entries(inferences)) { // eslint-disable-line
        if (inference.model.category === 'object_detection') {
          context.beginPath()
          for (const [_, properties] of Object.entries(inference.output)) { // eslint-disable-line
            const { location } = properties
            const x = location[0] * width
            const y = location[1] * height
            const w = (location[2] - location[0]) * width
            const h = (location[3] - location[1]) * height
            context.rect(x, y, w, h)
          }
          context.stroke()
        }
      }
      this.isImageLoaded = true
    },

    zoom_on_card(/* event */) {
      alert('Not Implemented') // eslint-disable-line
    }
  }
}
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
