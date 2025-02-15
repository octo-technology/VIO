<template>
  <v-app>
    <v-main>
      <v-container>
        <v-row v-if="fileName">
          <v-col cols="12">
            <p>Selected file: {{ fileName }}</p>
            <v-btn @click="submitConfig" color="primary">Submit Config</v-btn>
          </v-col>
        </v-row>
        <active-config-view v-if="showActiveConfig"></active-config-view>
        <all-configs-view v-if="showConfigs" @active-config-updated="fetchActiveConfig"></all-configs-view>
        <v-row v-else-if="showNewConfig">
          <v-col cols="12">
            <new-config-view ref="newConfig" @config-submitted="fetchConfigs"></new-config-view>
          </v-col>
        </v-row>
      </v-container>
    </v-main>
  </v-app>
</template>

<script>
import ApiService from '@/services/ApiService.js';
import NewConfigView from './NewConfigView.vue';
import ActiveConfigView from './ActiveConfigView.vue';
import AllConfigsView from './AllConfigsView.vue';

export default {
  name: 'ConfigView',
  components: {
    NewConfigView,
    ActiveConfigView,
    AllConfigsView
  },
  data() {
    return {
      showConfigs: true, // Boolean to toggle between viewing configs and creating a new config
      showActiveConfig: false, // Boolean to toggle between viewing active config
      showNewConfig: false, // Boolean to toggle between creating a new config
      fileName: '', // Store the name of the selected file
      snackbar: false,
      snackbarMessage: '',
      snackbarColor: '',
      snackbarTimeout: 3000
    };
  },
  methods: {
    triggerFileUpload() {
      this.$refs.fileInput.click();
    },
    handleFileUpload(event) {
      const file = event.target.files[0];
      if (file) {
        this.fileName = file.name;
        const reader = new FileReader();
        reader.onload = (e) => {
          try {
            const config = JSON.parse(e.target.result);
            this.$refs.newConfig.NewConfig = config;
            this.snackbarMessage = 'Config loaded successfully';
            this.snackbarColor = 'success';
          } catch (error) {
            this.snackbarMessage = 'Error loading config';
            this.snackbarColor = 'error';
            console.error('Error loading config:', error);
          }
          this.snackbar = true;
        };
        reader.readAsText(file);
      }
    },
    submitConfig() {
      const cleanedConfig = this.$refs.newConfig.cleanConfig(this.$refs.newConfig.NewConfig);
      ApiService.setActiveConfig(cleanedConfig)
        .then(response => {
          if (response.status === 200) {
            this.snackbarMessage = 'Config submitted successfully';
            this.snackbarColor = 'success';
            this.$refs.allConfigs.fetchConfigs(); // Refresh the configs
          } else {
            this.snackbarMessage = 'Error submitting config';
            this.snackbarColor = 'error';
          }
          this.snackbar = true;
        })
        .catch(error => {
          this.snackbarMessage = 'Error submitting config';
          this.snackbarColor = 'error';
          this.snackbar = true;
          console.error('Error submitting config:', error);
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