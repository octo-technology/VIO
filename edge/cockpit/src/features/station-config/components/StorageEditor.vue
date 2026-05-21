<template>
  <div class="text-subtitle-1 mb-2">Storage</div>
  <v-row dense align="center" class="mb-2">
    <v-col cols="12" sm="2">
      <v-select
        v-model="binaryStorageConfig.storage_type"
        :items="storageTypeItems"
        label="Binary type"
        density="compact"
        variant="outlined"
        hide-details
        @update:model-value="$emit('storage-type-change', binaryStorageConfig, $event)"
      />
    </v-col>
    <v-col v-if="binaryStorageConfig.storage_type !== 'filesystem'" cols="12" sm="4">
      <v-text-field
        v-model="binaryStorageConfig.bucket_name"
        :rules="[rules.required]"
        label="Bucket name"
        density="compact"
        variant="outlined"
        hide-details="auto"
      />
    </v-col>
    <v-col cols="12" :sm="binaryStorageConfig.storage_type !== 'filesystem' ? 6 : 10">
      <v-text-field
        v-model="binaryStorageConfig.target_directory"
        :rules="[rules.required]"
        label="Directory"
        density="compact"
        variant="outlined"
        hide-details="auto"
      />
    </v-col>
  </v-row>
  <v-row dense align="center">
    <v-col cols="12" sm="2">
      <v-select
        v-model="metadataStorageConfig.storage_type"
        :items="storageTypeItems"
        label="Metadata type"
        density="compact"
        variant="outlined"
        hide-details
        @update:model-value="$emit('storage-type-change', metadataStorageConfig, $event)"
      />
    </v-col>
    <v-col v-if="metadataStorageConfig.storage_type !== 'filesystem'" cols="12" sm="4">
      <v-text-field
        v-model="metadataStorageConfig.bucket_name"
        :rules="[rules.required]"
        label="Bucket name"
        density="compact"
        variant="outlined"
        hide-details="auto"
      />
    </v-col>
    <v-col cols="12" :sm="metadataStorageConfig.storage_type !== 'filesystem' ? 6 : 10">
      <v-text-field
        v-model="metadataStorageConfig.target_directory"
        :rules="[rules.required]"
        label="Directory"
        density="compact"
        variant="outlined"
        hide-details="auto"
      />
    </v-col>
  </v-row>
</template>

<script setup>
const binaryStorageConfig = defineModel('binaryStorageConfig', { type: Object, required: true })
const metadataStorageConfig = defineModel('metadataStorageConfig', { type: Object, required: true })

defineProps({
  storageTypeItems: { type: Array, required: true },
  rules: { type: Object, required: true },
})

defineEmits(['storage-type-change'])
</script>
