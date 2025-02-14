<template>
  <v-row>
    <v-col cols="12">
      <v-alert v-if="error" type="error" dismissible @input="error = false">
        {{ errorMessage }}
      </v-alert>
      <v-alert v-else-if="!activeConfig.station_name" type="info">
        No active config available
      </v-alert>
      <div v-else>
        <config-details :config="activeConfig"></config-details>
      </div>
    </v-col>
  </v-row>
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
          this.activeConfig = response.data;
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
/* Add any necessary styles here */
</style>