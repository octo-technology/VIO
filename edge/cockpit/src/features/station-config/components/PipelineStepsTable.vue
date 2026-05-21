<template>
  <div class="text-subtitle-1 mb-2">Pipeline steps</div>
  <v-table density="compact" class="mb-1">
    <thead>
      <tr>
        <th>Step</th>
        <th>Camera</th>
        <th>Model server URL</th>
        <th>Model</th>
        <th class="text-medium-emphasis">Version</th>
        <th>Camera rule</th>
        <th>Rule param</th>
        <th />
      </tr>
    </thead>
    <tbody>
      <tr v-for="(step, stepId) in pipelineSteps" :key="stepId">
        <td style="width:120px">
          <v-text-field
            :model-value="stepId"
            :rules="[rules.required, uniqueStepId(stepId)]"
            density="compact"
            variant="underlined"
            hide-details="auto"
            @update:model-value="(v) => $emit('rename-step', stepId, v)"
          />
        </td>
        <td style="width:140px">
          <v-select
            v-model="step.camera_id"
            :items="Object.keys(cameraConfigs)"
            :rules="[rules.required]"
            density="compact"
            variant="underlined"
            hide-details="auto"
          />
        </td>
        <td>
          <v-select
            :model-value="step.model_forwarder_config.model_serving_url"
            :items="modelServerUrls"
            :rules="[rules.required]"
            density="compact"
            variant="underlined"
            hide-details="auto"
            @update:model-value="(v) => $emit('serving-url-change', step, v)"
          />
        </td>
        <td>
          <v-combobox
            :model-value="step.model_forwarder_config.model_name"
            :items="modelsForUrl(step.model_forwarder_config.model_serving_url)"
            :rules="[rules.required]"
            density="compact"
            variant="underlined"
            hide-details="auto"
            hide-no-data
            @update:model-value="(v) => $emit('model-name-change', step, v)"
          />
        </td>
        <td style="width:80px" class="text-caption text-medium-emphasis">
          {{ step.model_forwarder_config.model_version || '—' }}
        </td>
        <td style="width:180px">
          <v-select
            :model-value="step.camera_rule_config?.camera_rule_type ?? 'none'"
            :items="cameraRuleItemsForStep(step)"
            density="compact"
            variant="underlined"
            hide-details
            @update:model-value="(v) => $emit('camera-rule-type-change', stepId, v)"
          />
        </td>
        <td style="min-width:180px">
          <template v-if="step.camera_rule_config">
            <v-combobox
              v-if="step.camera_rule_config.camera_rule_type === 'expected_label_rule'"
              v-model="step.camera_rule_config.expected_class"
              :items="classNamesForStep(step)"
              :rules="[rules.required]"
              placeholder="expected class"
              density="compact"
              variant="underlined"
              hide-details="auto"
              hide-no-data
            />
            <v-combobox
              v-else-if="step.camera_rule_config.camera_rule_type === 'unexpected_label_rule'"
              v-model="step.camera_rule_config.unexpected_class"
              :items="classNamesForStep(step)"
              :rules="[rules.required]"
              placeholder="unexpected class"
              density="compact"
              variant="underlined"
              hide-details="auto"
              hide-no-data
            />
            <template v-else>
              <v-combobox
                v-model="step.camera_rule_config.class_to_detect"
                :items="classNamesForStep(step)"
                :rules="[rules.required]"
                placeholder="class to detect"
                density="compact"
                variant="underlined"
                hide-details="auto"
                hide-no-data
              />
              <v-text-field
                v-model.number="step.camera_rule_config.threshold"
                :rules="[rules.positiveInt]"
                placeholder="threshold (n)"
                type="number"
                density="compact"
                variant="underlined"
                hide-details="auto"
              />
            </template>
          </template>
        </td>
        <td style="width:40px">
          <v-btn
            icon="mdi-delete-outline"
            size="x-small"
            variant="text"
            color="error"
            :disabled="Object.keys(pipelineSteps).length <= 1"
            @click="$emit('remove-step', stepId)"
          />
        </td>
      </tr>
    </tbody>
  </v-table>
  <div class="d-flex justify-end mb-4">
    <v-btn size="x-small" variant="tonal" prepend-icon="mdi-plus" @click="$emit('add-step')">Add step</v-btn>
  </div>
</template>

<script setup>
defineProps({
  pipelineSteps: { type: Object, required: true },
  cameraConfigs: { type: Object, required: true },
  modelServerUrls: { type: Array, required: true },
  modelsForUrl: { type: Function, required: true },
  classNamesForStep: { type: Function, required: true },
  cameraRuleItemsForStep: { type: Function, required: true },
  rules: { type: Object, required: true },
  uniqueStepId: { type: Function, required: true },
})

defineEmits(['rename-step', 'remove-step', 'add-step', 'serving-url-change', 'model-name-change', 'camera-rule-type-change'])
</script>
