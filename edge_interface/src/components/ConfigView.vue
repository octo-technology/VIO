<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-btn @click="showConfigs = true" color="primary">View All Configs</v-btn>
        <v-btn @click="showConfigs = false" color="secondary">Create New Config</v-btn>
      </v-col>
    </v-row>
    <v-row v-if="showConfigs">
    <v-col cols="12">
        <v-select
          v-model="selectedConfigs"
          :items="configOptions"
          label="Select Configs"
          multiple
          item-text="station_name"
          item-value="station_name"
        ></v-select>
      </v-col>
      <v-col v-for="config in filteredConfigs" :key="config.station_name" cols="12" md="6">
        <v-card>
          <v-card-title>{{ config.station_name }}</v-card-title>
          <v-card-text>
            <v-row>
              <v-col v-for="(cameraConfig, cameraId) in config.camera_configs" :key="cameraId" cols="12" md="6">
                <h3>Camera: {{ cameraId }}</h3>
                <p><strong>Camera ID:</strong> {{ cameraConfig.camera_id }}</p>
                <p><strong>Camera Type:</strong> {{ cameraConfig.camera_type }}</p>
                <p><strong>Source Directory:</strong> {{ cameraConfig.source_directory }}</p>
                <p><strong>Position:</strong> {{ cameraConfig.position }}</p>
                <h4>Model Forwarder Config</h4>
                <p><strong>Model Name:</strong> {{ cameraConfig.model_forwarder_config.model_name }}</p>
                <p><strong>Model Type:</strong> {{ cameraConfig.model_forwarder_config.model_type }}</p>
                <p><strong>Image Resolution:</strong> {{ cameraConfig.model_forwarder_config.image_resolution.width }}x{{ cameraConfig.model_forwarder_config.image_resolution.height }}</p>
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
      </v-col>
    </v-row>
    <v-row v-else>
      <v-col cols="12">
        <new-config-form @config-submitted="fetchConfigs"></new-config-form>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import ApiService from '@/services/ApiService.js';
import NewConfigForm from './NewConfigForm.vue';

export default {
  name: 'ConfigView',
  components: {
    NewConfigForm
  },
  data() {
    return {
      configs: [],
      selectedConfigs: [],
      showConfigs: true // Boolean to toggle between viewing configs and creating a new config
    };
  },
  created() {
    this.fetchConfigs();
  },
  computed: {
    configOptions() {
      return this.configs.map(config => config.station_name);
    },
    filteredConfigs() {
      return this.configs.filter(config => this.selectedConfigs.includes(config.station_name));
    }
  },
  methods: {
    fetchConfigs() {
      ApiService.getConfigs()
        .then(response => {
          // Transform the response data to an array of configs
          this.configs = Object.values(response.data);
        })
        .catch(error => {
          console.error('Error fetching configs:', error);
          this.configs = [];
        });
    }
  }
};
</script>

<style scoped>
/* Add any necessary styles here */
</style>