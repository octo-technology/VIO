<template>
  <v-container>
    <v-row justify="center">
      <v-col cols="12" class="d-flex justify-center">
        <v-select
          v-model="selectedConfigs"
          :items="configOptions"
          label="Select Configs"
          multiple
          item-text="station_name"
          item-value="station_name"
          class="max-width-500"
        ></v-select>
      </v-col>
    </v-row>
    <v-row v-if="error">
      <v-col cols="12">
        <v-alert type="error" dismissible @input="error = false">
          {{ errorMessage }}
        </v-alert>
      </v-col>
    </v-row>
    <v-row v-else>
      <v-col v-for="config in filteredConfigs" :key="config.station_name" cols="12" md="6">
        <v-card>
          <v-card-title class="d-flex justify-space-between align-center">
            <span>Config: {{ config.station_name }}</span>
            <v-btn @click="setActiveConfig(config.station_name)" small color="primary">Activate</v-btn>
          </v-card-title>
          <v-card-text>
            <config-details :config="config"></config-details>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <v-snackbar v-model="snackbar" :color="snackbarColor" :timeout="snackbarTimeout">
      {{ snackbarMessage }}
    </v-snackbar>
  </v-container>
</template>

<script>
import ApiService from '@/services/ApiService.js';
import ConfigDetails from './ConfigDetails.vue';

export default {
  name: 'AllConfigsView',
  components: {
    ConfigDetails
  },
  data() {
    return {
      configs: [],
      selectedConfigs: [],
      error: false,
      errorMessage: '',
      snackbar: false,
      snackbarMessage: '',
      snackbarColor: '',
      snackbarTimeout: 3000
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
          // Transform the response data to an array of configs and sort by name
          this.configs = Object.values(response.data).sort((a, b) => a.station_name.localeCompare(b.station_name));
        })
        .catch(error => {
          console.error('Error fetching configs:', error);
          const detail = error.response && error.response.data && error.response.data.detail;
          this.errorMessage = 'Error fetching configs: ' + (detail || error.message || 'Unknown error');
          this.error = true;
          this.configs = [];
        });
    },
    setActiveConfig(stationName) {
      ApiService.setActiveConfigByName(stationName)
        .then(response => {
          console.log('Active config set successfully:', response.data);
          this.snackbarMessage = 'Config activated successfully';
          this.snackbarColor = 'success';
          this.snackbar = true;
          this.$emit('active-config-updated'); // Emit an event to notify parent component
        })
        .catch(error => {
          console.error('Error setting active config:', error);
          this.snackbarMessage = 'Error setting active config';
          this.snackbarColor = 'error';
          this.snackbar = true;
        });
    }
  }
};
</script>

<style scoped>
.max-width-500 {
  max-width: 500px;
}
</style>