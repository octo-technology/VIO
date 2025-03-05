<!--TODO: https://vuetifyjs.com/en/components/expansion-panels/#custom-icon-->

<template>
  <v-container>
    <v-row>
      <v-col cols="12" class="d-flex justify-center">
        <v-alert v-model="snackbar" :type="snackbarColor" dismissible @input="snackbar = false" class="alert-box">
          {{ snackbarMessage }}
        </v-alert>
      </v-col>
    </v-row>
    <v-row v-if="!error">
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
      alert: true,
    };
  },
  created() {
    this.fetchConfigs();
    setTimeout(()=>{
      this.alert=false
    },5000)
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
          this.snackbarMessage = 'Error fetching configs: ' + (detail || error.message || 'Unknown error');
          this.snackbarColor = 'error';
          this.snackbar = true;
          this.configs = [];
        });
    },
    setActiveConfig(stationName) {
      ApiService.setActiveConfigByName(stationName)
        .then(response => {
          console.log('Active config set successfully:', response.data);
          this.snackbarMessage = `Config "${stationName}" activated successfully`;
          this.snackbarColor = 'success';
          this.snackbar = true;
          setTimeout(()=>{this.snackbar=false}, 3000);
        })
        .catch(error => {
          console.error('Error setting active config:', error);
          this.snackbarMessage = `Error setting active config "${stationName}"`;
          this.snackbarColor = 'error';
          this.snackbar = true;
        });
    }
  }
};
</script>

<style scoped>
.alert-box {
  max-width: 700px;
  width: 100%;
}

</style>