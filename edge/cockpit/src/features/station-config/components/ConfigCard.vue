<template>
  <v-card
    :variant="config.station_name === activeConfigName ? 'tonal' : 'outlined'"
    :color="config.station_name === activeConfigName ? 'primary' : undefined"
    height="100%"
    style="cursor:pointer"
    @click="$emit('edit', config)"
  >
    <v-card-title class="d-flex align-center gap-2 flex-wrap">
      {{ config.station_name }}
      <v-chip v-if="config.station_name === activeConfigName" size="x-small" color="primary" label>ACTIVE</v-chip>
    </v-card-title>
    <v-card-text class="text-caption text-medium-emphasis pb-1">
      {{ Object.keys(config.camera_configs).length }} camera(s) · {{ Object.keys(config.pipeline_steps).length }} pipeline step(s)
    </v-card-text>
    <v-card-actions @click.stop>
      <v-btn
        size="small"
        variant="tonal"
        :disabled="config.station_name === activeConfigName"
        :loading="activating === config.station_name"
        @click="$emit('activate', config.station_name)"
      >
        Activate
      </v-btn>
      <v-spacer />
      <v-btn icon="mdi-delete-outline" size="small" variant="text" color="error" @click="$emit('delete', config)" />
    </v-card-actions>
  </v-card>
</template>

<script setup>
defineProps({
  config: { type: Object, required: true },
  activeConfigName: { type: String, default: null },
  activating: { type: String, default: null },
})

defineEmits(['edit', 'activate', 'delete'])
</script>
