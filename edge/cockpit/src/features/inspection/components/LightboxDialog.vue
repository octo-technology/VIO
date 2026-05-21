<template>
  <v-dialog :model-value="modelValue" :max-width="1400" @keydown.esc="$emit('update:modelValue', false)">
    <div
      class="d-flex justify-center align-center bg-black"
      style="position:relative; min-height:200px; padding:40px 16px 16px"
      @click.self="$emit('update:modelValue', false)"
    >
      <v-btn
        icon="mdi-close"
        variant="text"
        color="white"
        style="position:absolute; top:4px; right:4px"
        @click="$emit('update:modelValue', false)"
      />

      <div style="position:relative; display:inline-block; line-height:0">
        <img
          :src="imgSrc"
          style="display:block; max-width:80vw; max-height:80vh; object-fit:contain"
        >

        <template v-for="{ stepId, step, pred } in predictions" :key="stepId">
          <div
            v-if="pred?.prediction_type === 'class'"
            style="position:absolute; bottom:12px; left:12px; pointer-events:none; z-index:10"
          >
            <v-chip
              :color="pred.label === 'OK' ? 'success' : pred.label === 'KO' ? 'error' : 'primary'"
              size="large"
              label
              style="font-size:1rem; font-weight:bold"
            >
              {{ pred.label }}
              <span v-if="pred.probability != null" class="ml-2">
                {{ (pred.probability * 100).toFixed(0) }}%
              </span>
            </v-chip>
          </div>

          <svg
            v-if="pred?.prediction_type === 'objects'"
            style="position:absolute; top:0; left:0; width:100%; height:100%; pointer-events:none; overflow:visible; z-index:10"
          >
            <g v-for="(obj, objId) in pred.detected_objects" :key="objId">
              <rect
                :x="bboxPct(obj.location, step).x + '%'"
                :y="bboxPct(obj.location, step).y + '%'"
                :width="bboxPct(obj.location, step).w + '%'"
                :height="bboxPct(obj.location, step).h + '%'"
                fill="none"
                stroke="lime"
                stroke-width="2"
              />
              <text
                :x="bboxPct(obj.location, step).x + '%'"
                :y="bboxPct(obj.location, step).y + '%'"
                font-size="14"
                font-weight="bold"
                fill="lime"
                stroke="black"
                stroke-width="3"
                paint-order="stroke fill"
                dominant-baseline="hanging"
              >{{ obj.label }} {{ (obj.objectness * 100).toFixed(0) }}%</text>
            </g>
          </svg>
        </template>
      </div>
    </div>
  </v-dialog>
</template>

<script setup>
import { bboxPct } from '../domain/bboxConverter'

defineProps({
  modelValue: { type: Boolean, required: true },
  imgSrc: { type: String, default: '' },
  predictions: { type: Array, default: () => [] },
})

defineEmits(['update:modelValue'])
</script>
