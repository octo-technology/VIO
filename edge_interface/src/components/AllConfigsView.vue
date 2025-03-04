<!--TODO: https://vuetifyjs.com/en/components/expansion-panels/#custom-icon-->

<template>
  <v-container>
    <v-row v-if="error">
      <v-col cols="12" class="d-flex justify-center">
        <v-alert type="error" dismissible @input="error = false" class="alert-box">
          {{ errorMessage }}
        </v-alert>
      </v-col>
    </v-row>
    <v-row v-else>
      <v-col cols="12">
        <v-expansion-panels popout>
          <v-expansion-panel v-for="config in configs" :key="config.station_name">
            <v-expansion-panel-header>
              <div class="d-flex justify-space-between align-center w-100">
                <span>{{ config.station_name }}</span>
                <v-icon @click.stop="setActiveConfig(config.station_name)" small color="primary">mdi-check</v-icon>
              </div>
            </v-expansion-panel-header>
            <v-expansion-panel-content>
              <config-details :config="config"></config-details>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-col>
    </v-row>
    <v-snackbar v-model="snackbar" :color="snackbarColor" :timeout="snackbarTimeout" class="snackbar-alert" top center>
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

.alert-box {
  max-width: 600px;
  width: 100%;
}

.snackbar-alert {
  max-width: 600px;
  width: 100%;
}
</style>