<template>
  <v-form @submit.prevent="submitConfig">
    <v-text-field v-model="newConfig.station_name" label="Station Name" required></v-text-field>
    <v-divider></v-divider>
    <h4>Camera Configs</h4>
    <div v-for="(cameraConfig, cameraId) in newConfig.camera_configs" :key="cameraId">
      <v-row>
        <v-col cols="12" md="6">
          <v-text-field v-model="cameraConfig.camera_id" label="Camera ID" required></v-text-field>
        </v-col>
        <v-col cols="12" md="6">
          <v-select
            v-model="cameraConfig.camera_type"
            :items="cameraTypes"
            label="Camera Type"
            required
          ></v-select>
        </v-col>
        <v-col cols="12" md="6" v-if="cameraConfig.camera_type === 'fake'">
          <v-text-field v-model="cameraConfig.source_directory" label="Source Directory" required></v-text-field>
        </v-col>
        <v-col cols="12" md="6">
          <v-text-field v-model="cameraConfig.position" label="Position" required></v-text-field>
        </v-col>
        <v-col cols="12">
          <h5>Model Forwarder Config</h5>
        </v-col>
        <v-col cols="12" md="6">
          <v-select
            v-model="cameraConfig.model_forwarder_config.model_name"
            :items="modelNames"
            label="Model Name"
            required
          ></v-select>
        </v-col>
        <v-col cols="12" md="6">
          <v-select
            v-model="cameraConfig.model_forwarder_config.model_type"
            :items="modelTypes"
            label="Model Type"
            required
          ></v-select>
        </v-col>
        <v-col cols="12" md="6">
          <v-text-field v-model="cameraConfig.model_forwarder_config.expected_image_resolution.width" label="Image Resolution Width" required></v-text-field>
        </v-col>
        <v-col cols="12" md="6">
          <v-text-field v-model="cameraConfig.model_forwarder_config.expected_image_resolution.height" label="Image Resolution Height" required></v-text-field>
        </v-col>
        <v-col cols="12" md="6">
          <v-text-field v-model="cameraConfig.model_forwarder_config.model_version" label="Model Version" required></v-text-field>
        </v-col>
        <v-col cols="12" md="6">
          <div v-for="(className, index) in cameraConfig.model_forwarder_config.class_names" :key="index">
            <v-text-field v-model="cameraConfig.model_forwarder_config.class_names[index]" label="Class Name" required></v-text-field>
            <v-btn @click="removeClassName(cameraId, index)" color="error" small>x</v-btn>
          </div>
          <v-btn @click="addClassName(cameraId)" color="primary" small>+</v-btn>
        </v-col>
        <v-col cols="12" md="6">
          <v-btn @click="toggleClassNamesFilepath(cameraId)" color="primary" small>
            {{ cameraConfig.showClassNamesFilepath ? 'Remove' : 'Add' }} Class Names Filepath
          </v-btn>
          <div v-if="cameraConfig.showClassNamesFilepath">
            <v-text-field v-model="cameraConfig.model_forwarder_config.class_names_filepath" label="Class Names Filepath"></v-text-field>
          </div>
        </v-col>
        <v-col cols="12" md="6">
          <v-text-field v-model="cameraConfig.model_forwarder_config.model_serving_url" label="Model Serving URL" required></v-text-field>
        </v-col>
        <v-col cols="12">
          <v-switch v-model="cameraConfig.model_forwarder_config.recreate_me" label="Recreate Me"></v-switch>
        </v-col>
        <v-col cols="12">
          <h5>Camera Rule Config</h5>
        </v-col>
        <v-col cols="12" md="6">
          <v-select
            v-model="cameraConfig.camera_rule_config.camera_rule_type"
            :items="cameraRuleTypes"
            label="Camera Rule Type"
            required
          ></v-select>
        </v-col>
        <v-col cols="12" md="6" v-if="cameraConfig.camera_rule_config.camera_rule_type === 'expected_label_rule'">
          <v-text-field v-model="cameraConfig.camera_rule_config.expected_class" label="Expected Class"></v-text-field>
        </v-col>
        <v-col cols="12" md="6" v-if="cameraConfig.camera_rule_config.camera_rule_type === 'unexpected_label_rule'">
          <v-text-field v-model="cameraConfig.camera_rule_config.unexpected_class" label="Unexpected Class"></v-text-field>
        </v-col>
        <v-col cols="12" md="6" v-if="cameraConfig.camera_rule_config.camera_rule_type === 'min_nb_objects_rule' || cameraConfig.camera_rule_config.camera_rule_type === 'max_nb_objects_rule'">
          <v-text-field v-model="cameraConfig.camera_rule_config.class_to_detect" label="Class to Detect"></v-text-field>
        </v-col>
        <v-col cols="12" md="6" v-if="cameraConfig.camera_rule_config.camera_rule_type === 'min_nb_objects_rule' || cameraConfig.camera_rule_config.camera_rule_type === 'max_nb_objects_rule'">
          <v-text-field v-model="cameraConfig.camera_rule_config.threshold" label="Threshold" required></v-text-field>
        </v-col>
        <v-col cols="12">
          <v-switch v-model="cameraConfig.camera_rule_config.recreate_me" label="Recreate Me"></v-switch>
        </v-col>
        <v-col cols="12">
          <v-btn @click="removeCameraConfig(cameraId)" color="error" small>x</v-btn>
        </v-col>
      </v-row>
      <v-divider></v-divider>
    </div>
    <v-btn @click="showAddCameraDialog = true" color="primary" small>+ Add Camera</v-btn>
    <h4>Binary Storage Config</h4>
    <v-select
      v-model="newConfig.binary_storage_config.storage_type"
      :items="storageTypes"
      label="Storage Type"
      required
    ></v-select>
    <v-text-field v-model="newConfig.binary_storage_config.target_directory" label="Target Directory" required></v-text-field>
    <v-btn @click="toggleBinaryPrefix" color="primary" small>
      {{ showBinaryPrefix ? 'Remove' : 'Add' }} Prefix
    </v-btn>
    <div v-if="showBinaryPrefix">
      <v-text-field v-model="newConfig.binary_storage_config.prefix" label="Prefix"></v-text-field>
    </div>
    <v-switch v-model="newConfig.binary_storage_config.recreate_me" label="Recreate Me"></v-switch>
    <v-btn @click="toggleBinaryCloudStorage" color="primary" small>
      {{ showBinaryCloudStorage ? 'Remove' : 'Add' }} Cloud Storage Credentials
    </v-btn>
    <div v-if="showBinaryCloudStorage">
      <h5>Cloud Storage Credentials</h5>
      <v-text-field v-model="newConfig.binary_storage_config.cloud_storage_creds.aws_access_key_id" label="AWS Access Key ID"></v-text-field>
      <v-text-field v-model="newConfig.binary_storage_config.cloud_storage_creds.aws_secret_access_key" label="AWS Secret Access Key"></v-text-field>
      <v-text-field v-model="newConfig.binary_storage_config.cloud_storage_creds.aws_session_token" label="AWS Session Token"></v-text-field>
      <v-text-field v-model="newConfig.binary_storage_config.cloud_storage_creds.bucket_name" label="Bucket Name"></v-text-field>
    </div>
    <v-divider></v-divider>
    <h4>Metadata Storage Config</h4>
    <v-select
      v-model="newConfig.metadata_storage_config.storage_type"
      :items="storageTypes"
      label="Storage Type"
      required
    ></v-select>
    <v-text-field v-model="newConfig.metadata_storage_config.target_directory" label="Target Directory" required></v-text-field>
    <v-btn @click="toggleMetadataPrefix" color="primary" small>
      {{ showMetadataPrefix ? 'Remove' : 'Add' }} Prefix
    </v-btn>
    <div v-if="showMetadataPrefix">
      <v-text-field v-model="newConfig.metadata_storage_config.prefix" label="Prefix"></v-text-field>
    </div>
    <v-switch v-model="newConfig.metadata_storage_config.recreate_me" label="Recreate Me"></v-switch>
    <v-btn @click="toggleMetadataCloudStorage" color="primary" small>
      {{ showMetadataCloudStorage ? 'Remove' : 'Add' }} Cloud Storage Credentials
    </v-btn>
    <div v-if="showMetadataCloudStorage">
      <h5>Cloud Storage Credentials</h5>
      <v-text-field v-model="newConfig.metadata_storage_config.cloud_storage_creds.aws_access_key_id" label="AWS Access Key ID"></v-text-field>
      <v-text-field v-model="newConfig.metadata_storage_config.cloud_storage_creds.aws_secret_access_key" label="AWS Secret Access Key"></v-text-field>
      <v-text-field v-model="newConfig.metadata_storage_config.cloud_storage_creds.aws_session_token" label="AWS Session Token"></v-text-field>
      <v-text-field v-model="newConfig.metadata_storage_config.cloud_storage_creds.bucket_name" label="Bucket Name"></v-text-field>
    </div>
    <v-divider></v-divider>
    <h4>Item Rule Config</h4>
    <v-select
      v-model="newConfig.item_rule_config.item_rule_type"
      :items="itemRuleTypes"
      label="Item Rule Type"
      required
    ></v-select>
    <v-text-field v-model="newConfig.item_rule_config.expected_decision" label="Expected Decision" required></v-text-field>
    <v-text-field v-model="newConfig.item_rule_config.threshold" label="Threshold" required></v-text-field>
    <v-switch v-model="newConfig.item_rule_config.recreate_me" label="Recreate Me"></v-switch>
    <v-btn type="submit" color="primary">Submit</v-btn>

    <!-- Add Camera Dialog -->
    <v-dialog v-model="showAddCameraDialog" max-width="500px">
      <v-card>
        <v-card-title>
          <span class="headline">Add Camera</span>
        </v-card-title>
        <v-card-text>
          <v-text-field v-model="newCameraId" label="Camera ID" required></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="blue darken-1" text @click="showAddCameraDialog = false">Cancel</v-btn>
          <v-btn color="blue darken-1" text @click="addCameraConfig">Add</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
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
        camera_configs: {},
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
      },
      cameraTypes: ['fake', 'usb', 'raspberry', 'webcam'],
      modelTypes: ['fake', 'classification', 'object_detection', 'segmentation'],
      cameraRuleTypes: ['expected_label_rule', 'unexpected_label_rule', 'min_nb_objects_rule', 'max_nb_objects_rule'],
      modelNames: ['fake_model', 'marker_quality_control', 'pin_detection', 'mobilenet_ssd_v2_coco', 'mobilenet_ssd_v2_face', 'yolo_coco_nano'],
      storageTypes: ['filesystem', 'aws', 'azure', 'gcp'],
      itemRuleTypes: ['min_threshold_ratio_rule', 'min_threshold_rule'],
      showBinaryCloudStorage: false,
      showMetadataCloudStorage: false,
      showBinaryPrefix: false,
      showMetadataPrefix: false,
      showAddCameraDialog: false,
      newCameraId: ''
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
    },
    addCameraConfig() {
      if (!this.newCameraId) {
        alert('Camera ID is required');
        return;
      }
      const newCameraConfig = {
        camera_id: this.newCameraId,
        camera_type: 'webcam',
        position: 'front',
        model_forwarder_config: {
          model_name: 'marker_quality_control',
          model_type: 'classification',
          expected_image_resolution: {
            width: 320,
            height: 320
          },
          model_version: '1',
          class_names: ['OK', 'KO'],
          class_names_filepath: '',
          model_serving_url: 'http://edge_model_serving:8501/',
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
      };
      this.$set(this.newConfig.camera_configs, this.newCameraId, newCameraConfig);
      this.newCameraId = '';
      this.showAddCameraDialog = false;
    },
    removeCameraConfig(cameraId) {
      this.$delete(this.newConfig.camera_configs, cameraId);
    },
    addClassName(cameraId) {
      this.newConfig.camera_configs[cameraId].model_forwarder_config.class_names.push('');
    },
    removeClassName(cameraId, index) {
      this.newConfig.camera_configs[cameraId].model_forwarder_config.class_names.splice(index, 1);
    },
    toggleBinaryCloudStorage() {
      this.showBinaryCloudStorage = !this.showBinaryCloudStorage;
    },
    toggleMetadataCloudStorage() {
      this.showMetadataCloudStorage = !this.showMetadataCloudStorage;
    },
    toggleClassNamesFilepath(cameraId) {
      this.$set(this.newConfig.camera_configs[cameraId], 'showClassNamesFilepath', !this.newConfig.camera_configs[cameraId].showClassNamesFilepath);
    },
    toggleBinaryPrefix() {
      this.showBinaryPrefix = !this.showBinaryPrefix;
    },
    toggleMetadataPrefix() {
      this.showMetadataPrefix = !this.showMetadataPrefix;
    }
  }
};
</script>

<style scoped>
/* Add any necessary styles here */
</style>