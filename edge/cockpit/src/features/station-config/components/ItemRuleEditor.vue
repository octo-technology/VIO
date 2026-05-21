<template>
  <div class="text-subtitle-1 mb-2">Item rule</div>
  <v-row class="mb-4" align="center">
    <v-col cols="12" sm="4" md="3">
      <v-select
        :model-value="itemRuleConfig?.item_rule_type ?? 'none'"
        :items="itemRuleTypeItems"
        label="Rule type"
        density="compact"
        variant="outlined"
        hide-details
        @update:model-value="$emit('set-item-rule-type', $event)"
      />
    </v-col>
    <template v-if="itemRuleConfig">
      <v-col cols="12" sm="3" md="2">
        <v-select
          v-model="itemRuleConfig.expected_decision"
          :items="['OK', 'KO']"
          label="Expected decision"
          density="compact"
          variant="outlined"
          hide-details
        />
      </v-col>
      <v-col cols="12" sm="3" md="2">
        <v-text-field
          v-model.number="itemRuleConfig.threshold"
          :rules="itemRuleConfig.item_rule_type === 'min_threshold_ratio_rule' ? [rules.ratio] : [rules.positiveInt]"
          :label="itemRuleConfig.item_rule_type === 'min_threshold_ratio_rule' ? 'Ratio (0–1)' : 'Min count'"
          type="number"
          density="compact"
          variant="outlined"
          hide-details="auto"
        />
      </v-col>
    </template>
  </v-row>
</template>

<script setup>
const itemRuleConfig = defineModel('itemRuleConfig', { type: Object, default: null })

defineProps({
  itemRuleTypeItems: { type: Array, required: true },
  rules: { type: Object, required: true },
})

defineEmits(['set-item-rule-type'])
</script>
