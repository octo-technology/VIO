<template>
  <div>
    <v-card>
      <v-card-text>
        <v-row>
          <v-col v-for="(cameraConfig, index) in config.camera_configs" :key="index" cols="12" md="6">
            <h2>Camera: {{ cameraConfig.camera_id }}</h2>
            <v-list dense>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Camera ID</v-list-item-title>
                  <v-list-item-subtitle>{{ cameraConfig.camera_id }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Camera Type</v-list-item-title>
                  <v-list-item-subtitle>{{ cameraConfig.camera_type }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item v-if="cameraConfig.source_directory">
                <v-list-item-content>
                  <v-list-item-title>Source Directory</v-list-item-title>
                  <v-list-item-subtitle>{{ cameraConfig.source_directory }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item v-if="cameraConfig.camera_resolution">
                <v-list-item-content>
                  <v-list-item-title>Camera Resolution</v-list-item-title>
                  <v-list-item-subtitle>{{ cameraConfig.camera_resolution.width }}x{{ cameraConfig.camera_resolution.height }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Position</v-list-item-title>
                  <v-list-item-subtitle>{{ cameraConfig.position }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item v-if="cameraConfig.recreate_me">
                <v-list-item-content>
                  <v-list-item-title>Recreate Camera</v-list-item-title>
                  <v-list-item-subtitle>{{ cameraConfig.recreate_me }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
            <h3>Model Forwarder Config</h3>
            <v-list dense>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Model Name</v-list-item-title>
                  <v-list-item-subtitle>{{ cameraConfig.model_forwarder_config.model_name }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Model Type</v-list-item-title>
                  <v-list-item-subtitle>{{ cameraConfig.model_forwarder_config.model_type }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Expected Image Resolution</v-list-item-title>
                  <v-list-item-subtitle>{{ cameraConfig.model_forwarder_config.expected_image_resolution.width }}x{{ cameraConfig.model_forwarder_config.expected_image_resolution.height }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Model Version</v-list-item-title>
                  <v-list-item-subtitle>{{ cameraConfig.model_forwarder_config.model_version }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Class Names</v-list-item-title>
                  <v-list-item-subtitle>{{ cameraConfig.model_forwarder_config.class_names.join(', ') }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Model Serving URL</v-list-item-title>
                  <v-list-item-subtitle>{{ cameraConfig.model_forwarder_config.model_serving_url }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Model ID</v-list-item-title>
                  <v-list-item-subtitle>{{ cameraConfig.model_forwarder_config.model_id }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item v-if="cameraConfig.model_forwarder_config.recreate_me">
                <v-list-item-content>
                  <v-list-item-title>Recreate Model</v-list-item-title>
                  <v-list-item-subtitle>{{ cameraConfig.model_forwarder_config.recreate_me }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
            <h3>Camera Rule Config</h3>
            <v-list dense v-if="cameraConfig.camera_rule_config">
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Rule Type</v-list-item-title>
                  <v-list-item-subtitle>{{ cameraConfig.camera_rule_config.camera_rule_type }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item v-if="cameraConfig.camera_rule_config.expected_class">
                <v-list-item-content>
                  <v-list-item-title>Expected Class</v-list-item-title>
                  <v-list-item-subtitle>{{ cameraConfig.camera_rule_config.expected_class }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item v-if="cameraConfig.camera_rule_config.unexpected_class">
                <v-list-item-content>
                  <v-list-item-title>Unexpected Class</v-list-item-title>
                  <v-list-item-subtitle>{{ cameraConfig.camera_rule_config.unexpected_class }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item v-if="cameraConfig.camera_rule_config.class_to_detect">
                <v-list-item-content>
                  <v-list-item-title>Class to Detect</v-list-item-title>
                  <v-list-item-subtitle>{{ cameraConfig.camera_rule_config.class_to_detect }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item v-if="cameraConfig.camera_rule_config.threshold">
                <v-list-item-content>
                  <v-list-item-title>Threshold</v-list-item-title>
                  <v-list-item-subtitle>{{ cameraConfig.camera_rule_config.threshold }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item v-if="cameraConfig.camera_rule_config.recreate_me">
                <v-list-item-content>
                  <v-list-item-title>Recreate Rule</v-list-item-title>
                  <v-list-item-subtitle>{{ cameraConfig.camera_rule_config.recreate_me }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-col>
        </v-row>
        <v-divider></v-divider>
        <p></p>
        <v-row>
          <v-col cols="12" md="6">
            <h3>Binary Storage Config</h3>
            <v-list dense>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Storage Type</v-list-item-title>
                  <v-list-item-subtitle>{{ config.binary_storage_config.storage_type }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Target Directory</v-list-item-title>
                  <v-list-item-subtitle>{{ config.binary_storage_config.target_directory }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item v-if="config.binary_storage_config.recreate_me">
                <v-list-item-content>
                  <v-list-item-title>Recreate Binary Storage</v-list-item-title>
                  <v-list-item-subtitle>{{ config.binary_storage_config.recreate_me }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-col>
          <v-col cols="12" md="6">
            <h3>Metadata Storage Config</h3>
            <v-list dense>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Storage Type</v-list-item-title>
                  <v-list-item-subtitle>{{ config.metadata_storage_config.storage_type }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Target Directory</v-list-item-title>
                  <v-list-item-subtitle>{{ config.metadata_storage_config.target_directory }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item v-if="config.metadata_storage_config.recreate_me">
                <v-list-item-content>
                  <v-list-item-title>Recreate Metadata Storage</v-list-item-title>
                  <v-list-item-subtitle>{{ config.metadata_storage_config.recreate_me }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-col>
        </v-row>
        <v-divider></v-divider>
        <p></p>
        <h3>Item Rule Config</h3>
        <v-list dense v-if="config.item_rule_config">
          <v-list-item>
            <v-list-item-content>
              <v-list-item-title>Rule Type</v-list-item-title>
              <v-list-item-subtitle>{{ config.item_rule_config.item_rule_type }}</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
          <v-list-item>
            <v-list-item-content>
              <v-list-item-title>Expected Decision</v-list-item-title>
              <v-list-item-subtitle>{{ config.item_rule_config.expected_decision }}</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
          <v-list-item>
            <v-list-item-content>
              <v-list-item-title>Threshold</v-list-item-title>
              <v-list-item-subtitle>{{ config.item_rule_config.threshold }}</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
          <v-list-item v-if="config.item_rule_config.recreate_me">
            <v-list-item-content>
              <v-list-item-title>Recreate Item Rule</v-list-item-title>
              <v-list-item-subtitle>{{ config.item_rule_config.recreate_me }}</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </v-list>
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