<template>
  <v-chip :color="itemChipColor(item)" size="small" label>
    {{ itemChipLabel(item) }}
  </v-chip>
</template>

<script setup>
import { itemChipColor, itemChipLabel } from '../domain/itemDecision'

defineProps({ item: { type: Object, required: true } })
</script>
