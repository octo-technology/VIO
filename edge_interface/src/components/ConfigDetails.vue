<template>
  <div>
    <h3>Active Config: {{ config.station_name }}</h3>
    <v-card>
      <v-card-text>
        <v-row>
          <v-col v-for="(cameraConfig, cameraId) in config.camera_configs" :key="cameraId" cols="12" md="6">
            <h4>Camera: {{ cameraId }}</h4>
            <p><strong>Camera ID:</strong> {{ cameraConfig.camera_id }}</p>
            <p><strong>Camera Type:</strong> {{ cameraConfig.camera_type }}</p>
            <p v-if="cameraConfig.source_directory"><strong>Source Directory:</strong> {{ cameraConfig.source_directory }}</p>
            <p v-if="cameraConfig.camera_resolution"><strong>Camera Resolution:</strong> {{ cameraConfig.camera_resolution.width }}x{{ cameraConfig.camera_resolution.height }}</p>
            <p><strong>Position:</strong> {{ cameraConfig.position }}</p>
            <h4>Model Forwarder Config</h4>
            <p><strong>Model Name:</strong> {{ cameraConfig.model_forwarder_config.model_name }}</p>
            <p><strong>Model Type:</strong> {{ cameraConfig.model_forwarder_config.model_type }}</p>
            <p><strong>Expected Image Resolution:</strong> {{ cameraConfig.model_forwarder_config.expected_image_resolution.width }}x{{ cameraConfig.model_forwarder_config.expected_image_resolution.height }}</p>
            <p><strong>Model Version:</strong> {{ cameraConfig.model_forwarder_config.model_version }}</p>
            <p><strong>Class Names:</strong> {{ cameraConfig.model_forwarder_config.class_names.join(', ') }}</p>
            <p><strong>Model Serving URL:</strong> {{ cameraConfig.model_forwarder_config.model_serving_url }}</p>
            <p><strong>Model ID:</strong> {{ cameraConfig.model_forwarder_config.model_id }}</p>
            <h4>Camera Rule Config</h4>
            <pre>{{ cameraConfig.camera_rule_config }}</pre>
          </v-col>
        </v-row>
        <v-divider></v-divider>
        <v-row>
          <v-col cols="12" md="6">
            <h4>Binary Storage Config</h4>
            <pre>{{ config.binary_storage_config }}</pre>
          </v-col>
          <v-col cols="12" md="6">
            <h4>Metadata Storage Config</h4>
            <pre>{{ config.metadata_storage_config }}</pre>
          </v-col>
        </v-row>
        <v-divider></v-divider>
        <h4>Item Rule Config</h4>
        <pre>{{ config.item_rule_config }}</pre>
      </v-card-text>
    </v-card>
  </div>
</template>

<script>
export default {
  name: 'ConfigDetails',
  props: {
    config: {
      type: Object,
      required: true
    }
  }
};
</script>

<style scoped>
/* Add any necessary styles here */
</style>