<template>
  <v-container>
    <v-row>
      <v-col cols="12" class="d-flex justify-center">
        <v-alert v-if="error" type="error" dismissible @input="error = false" class="alert-box">
          {{ errorMessage }}
        </v-alert>
        <v-alert v-else-if="!activeConfig.station_name" type="info" class="alert-box">
          No active config available
        </v-alert>
        <v-card v-else>
          <v-card-title>Active Config: {{ activeConfig.station_name }}</v-card-title>
          <v-card-text>
            <config-details :config="activeConfig"></config-details>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import ApiService from '@/services/ApiService.js';
import ConfigDetails from './ConfigDetails.vue';

export default {
  name: 'ActiveConfigView',
  components: {
    ConfigDetails
  },
  data() {
    return {
      activeConfig: {},
      error: false,
      errorMessage: ''
    };
  },
  created() {
    this.fetchActiveConfig();
  },
  methods: {
    fetchActiveConfig() {
      ApiService.getActiveConfig()
        .then(response => {
          if (response.data && response.data.station_name) {
            this.activeConfig = response.data;
            this.error = false;
          } else {
            this.activeConfig = {};
            this.errorMessage = 'No active config available';
            this.error = true;
          }
        })
        .catch(error => {
          console.error('Error fetching active config:', error);
          const detail = error.response && error.response.data && error.response.data.detail;
          this.errorMessage = 'Error fetching active config: ' + (detail || error.message || 'Unknown error');
          this.error = true;
          this.activeConfig = {};
        });
    }
  }
};
</script>

<style scoped>
.alert-box {
  max-width: 600px;
  /* Adjust the width as needed */
  width: 100%;
}
</style>