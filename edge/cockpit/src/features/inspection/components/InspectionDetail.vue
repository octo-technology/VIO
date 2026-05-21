<template>
  <div class="d-flex align-center gap-3 mb-4 flex-wrap">
    <v-btn variant="text" prepend-icon="mdi-arrow-left" @click="$emit('back')">
      Recent Inspections
    </v-btn>
    <v-divider vertical class="mx-1" style="height:24px" />
    <span class="text-truncate font-weight-medium" style="max-width:400px">{{ item?.id }}</span>
    <v-chip v-if="item" :color="itemChipColor(item)" size="small" label>
      {{ itemChipLabel(item) }}
    </v-chip>
    <v-progress-circular v-if="polling" indeterminate size="18" width="2" />
    <span v-if="item?.creation_date" class="text-caption text-medium-emphasis ml-auto">
      {{ new Date(item.creation_date).toLocaleString() }}
    </span>
  </div>

  <v-progress-linear v-if="loadingDetail" indeterminate class="mb-4" />

  <div class="text-subtitle-2 mb-2">Images</div>
  <v-row class="mb-4">
    <v-col
      v-for="(_, cameraId) in item?.cameras_metadata"
      :key="cameraId"
      cols="12"
      sm="6"
      md="4"
    >
      <v-card variant="outlined" style="cursor:zoom-in" @click="$emit('open-lightbox', cameraId)">
        <v-card-subtitle>{{ cameraId }}</v-card-subtitle>
        <v-img :src="itemImageUrl(item.id, cameraId)" height="200" cover>
          <template #error>
            <v-sheet height="200" class="d-flex align-center justify-center text-medium-emphasis">
              No image
            </v-sheet>
          </template>
        </v-img>
      </v-card>
    </v-col>
  </v-row>

  <div v-if="stationConfig?.pipeline_steps">
    <div class="text-subtitle-2 mb-2">Pipeline results</div>
    <v-table density="compact" class="mb-4">
      <thead>
        <tr>
          <th>Step</th>
          <th>Camera</th>
          <th>Prediction</th>
          <th>Rule</th>
          <th>Result</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(step, stepId) in stationConfig.pipeline_steps" :key="stepId">
          <td>{{ stepId }}</td>
          <td>{{ step.camera_id }}</td>
          <td>{{ predictionText(item?.predictions?.[stepId]) }}</td>
          <td class="text-caption text-medium-emphasis">{{ cameraRuleText(step.camera_rule_config) ?? '—' }}</td>
          <td>
            <template v-if="step.camera_rule_config && item?.predictions?.[stepId]">
              <v-chip
                :color="cameraRuleResult(step.camera_rule_config, item.predictions[stepId]) === 'OK' ? 'success' : 'error'"
                size="x-small"
                label
              >
                {{ cameraRuleResult(step.camera_rule_config, item.predictions[stepId]) }}
              </v-chip>
            </template>
            <span v-else class="text-medium-emphasis">—</span>
          </td>
        </tr>
      </tbody>
    </v-table>

    <div class="text-subtitle-2 mb-2">Final decision rule</div>
    <v-chip size="small" variant="tonal" prepend-icon="mdi-scale-balance">
      {{ itemRuleText(stationConfig.item_rule_config) ?? 'No item rule defined' }}
    </v-chip>
  </div>
</template>

<script setup>
import { itemChipColor, itemChipLabel } from '../domain/itemDecision'
import { predictionText } from '../domain/predictionFormatter'
import { cameraRuleText, cameraRuleResult } from '../../station-config/domain/cameraRuleEvaluator'
import { itemRuleText } from '../../station-config/domain/itemRuleFormatter'

defineProps({
  item: { type: Object, default: null },
  stationConfig: { type: Object, default: null },
  polling: { type: Boolean, default: false },
  loadingDetail: { type: Boolean, default: false },
  itemImageUrl: { type: Function, required: true },
})

defineEmits(['back', 'open-lightbox'])
</script>
