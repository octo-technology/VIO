<template>
  <v-form @submit.prevent="submitConfig">
    <v-text-field v-model="newConfig.station_name" label="Station Name" required></v-text-field>
    <v-divider></v-divider>
    <h4>Camera Configs</h4>
    <div v-for="(cameraConfig, cameraId) in newConfig.camera_configs" :key="cameraId">
      <v-text-field v-model="cameraConfig.camera_id" label="Camera ID" required></v-text-field>
      <v-text-field v-model="cameraConfig.camera_type" label="Camera Type" required></v-text-field>
      <v-text-field v-model="cameraConfig.source_directory" label="Source Directory" required></v-text-field>
      <v-text-field v-model="cameraConfig.position" label="Position" required></v-text-field>
      <h5>Model Forwarder Config</h5>
      <v-text-field v-model="cameraConfig.model_forwarder_config.model_name" label="Model Name" required></v-text-field>
      <v-text-field v-model="cameraConfig.model_forwarder_config.model_type" label="Model Type" required></v-text-field>
      <v-text-field v-model="cameraConfig.model_forwarder_config.image_resolution.width" label="Image Resolution Width" required></v-text-field>
      <v-text-field v-model="cameraConfig.model_forwarder_config.image_resolution.height" label="Image Resolution Height" required></v-text-field>
      <v-text-field v-model="cameraConfig.model_forwarder_config.model_version" label="Model Version" required></v-text-field>
      <v-text-field v-model="cameraConfig.model_forwarder_config.class_names" label="Class Names" required></v-text-field>
      <v-text-field v-model="cameraConfig.model_forwarder_config.class_names_filepath" label="Class Names Filepath"></v-text-field>
      <v-text-field v-model="cameraConfig.model_forwarder_config.model_serving_url" label="Model Serving URL" required></v-text-field>
      <v-switch v-model="cameraConfig.model_forwarder_config.recreate_me" label="Recreate Me"></v-switch>
      <h5>Camera Rule Config</h5>
      <v-text-field v-model="cameraConfig.camera_rule_config.camera_rule_type" label="Camera Rule Type" required></v-text-field>
      <v-text-field v-model="cameraConfig.camera_rule_config.expected_class" label="Expected Class"></v-text-field>
      <v-text-field v-model="cameraConfig.camera_rule_config.unexpected_class" label="Unexpected Class"></v-text-field>
      <v-text-field v-model="cameraConfig.camera_rule_config.class_to_detect" label="Class to Detect"></v-text-field>
      <v-text-field v-model="cameraConfig.camera_rule_config.threshold" label="Threshold" required></v-text-field>
      <v-switch v-model="cameraConfig.camera_rule_config.recreate_me" label="Recreate Me"></v-switch>
      <v-divider></v-divider>
    </div>
    <h4>Binary Storage Config</h4>
    <v-text-field v-model="newConfig.binary_storage_config.storage_type" label="Storage Type" required></v-text-field>
    <v-text-field v-model="newConfig.binary_storage_config.target_directory" label="Target Directory" required></v-text-field>
    <v-text-field v-model="newConfig.binary_storage_config.prefix" label="Prefix" required></v-text-field>
    <v-switch v-model="newConfig.binary_storage_config.recreate_me" label="Recreate Me"></v-switch>
    <h5>Cloud Storage Credentials</h5>
    <v-text-field v-model="newConfig.binary_storage_config.cloud_storage_creds.aws_access_key_id" label="AWS Access Key ID"></v-text-field>
    <v-text-field v-model="newConfig.binary_storage_config.cloud_storage_creds.aws_secret_access_key" label="AWS Secret Access Key"></v-text-field>
    <v-text-field v-model="newConfig.binary_storage_config.cloud_storage_creds.aws_session_token" label="AWS Session Token"></v-text-field>
    <v-text-field v-model="newConfig.binary_storage_config.cloud_storage_creds.bucket_name" label="Bucket Name"></v-text-field>
    <v-divider></v-divider>
    <h4>Metadata Storage Config</h4>
    <v-text-field v-model="newConfig.metadata_storage_config.storage_type" label="Storage Type" required></v-text-field>
    <v-text-field v-model="newConfig.metadata_storage_config.target_directory" label="Target Directory" required></v-text-field>
    <v-text-field v-model="newConfig.metadata_storage_config.prefix" label="Prefix" required></v-text-field>
    <v-switch v-model="newConfig.metadata_storage_config.recreate_me" label="Recreate Me"></v-switch>
    <h5>Cloud Storage Credentials</h5>
    <v-text-field v-model="newConfig.metadata_storage_config.cloud_storage_creds.aws_access_key_id" label="AWS Access Key ID"></v-text-field>
    <v-text-field v-model="newConfig.metadata_storage_config.cloud_storage_creds.aws_secret_access_key" label="AWS Secret Access Key"></v-text-field>
    <v-text-field v-model="newConfig.metadata_storage_config.cloud_storage_creds.aws_session_token" label="AWS Session Token"></v-text-field>
    <v-text-field v-model="newConfig.metadata_storage_config.cloud_storage_creds.bucket_name" label="Bucket Name"></v-text-field>
    <v-divider></v-divider>
    <h4>Item Rule Config</h4>
    <v-text-field v-model="newConfig.item_rule_config.item_rule_type" label="Item Rule Type" required></v-text-field>
    <v-text-field v-model="newConfig.item_rule_config.expected_decision" label="Expected Decision" required></v-text-field>
    <v-text-field v-model="newConfig.item_rule_config.threshold" label="Threshold" required></v-text-field>
    <v-switch v-model="newConfig.item_rule_config.recreate_me" label="Recreate Me"></v-switch>
    <v-btn type="submit" color="primary">Submit</v-btn>
  </v-form>
</template>

<script>
import ApiService from '@/services/ApiService.js';

export default {
  name: 'NewConfigForm',
  data() {
    return {
      newConfig: {
        station_name: '',
        camera_configs: {
          additionalProp1: {
            camera_id: '',
            camera_type: 'fake',
            source_directory: '',
            position: 'front',
            model_forwarder_config: {
              model_name: 'fake_model',
              model_type: 'fake',
              image_resolution: {
                width: 1,
                height: 1
              },
              model_version: '',
              class_names: [''],
              class_names_filepath: '',
              model_serving_url: 'https://example.com/',
              recreate_me: false
            },
            camera_rule_config: {
              camera_rule_type: 'expected_label_rule',
              expected_class: '',
              unexpected_class: '',
              class_to_detect: '',
              threshold: 1,
              recreate_me: false
            },
            recreate_me: false
          }
        },
        binary_storage_config: {
          storage_type: 'filesystem',
          target_directory: 'data_storage',
          prefix: '',
          recreate_me: false,
          cloud_storage_creds: {
            aws_access_key_id: '',
            aws_secret_access_key: '',
            aws_session_token: '',
            bucket_name: ''
          }
        },
        metadata_storage_config: {
          storage_type: 'filesystem',
          target_directory: 'data_storage',
          prefix: '',
          recreate_me: false,
          cloud_storage_creds: {
            aws_access_key_id: '',
            aws_secret_access_key: '',
            aws_session_token: '',
            bucket_name: ''
          }
        },
        item_rule_config: {
          item_rule_type: 'min_threshold_ratio_rule',
          expected_decision: 'KO',
          threshold: 0,
          recreate_me: false
        }
      }
    };
  },
  methods: {
    submitConfig() {
      ApiService.setActiveConfig(this.newConfig)
        .then(response => {
          console.log('Config submitted successfully:', response.data);
          this.$emit('config-submitted'); // Emit an event to notify the parent component
        })
        .catch(error => {
          console.error('Error submitting config:', error);
        });
    }
  }
};
</script>

<style scoped>
/* Add any necessary styles here */
</style>