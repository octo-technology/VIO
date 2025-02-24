<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="d-flex justify-center align-center">
            <v-btn @click="triggerApi" class="ml-4 trigger-button">
              <span>Trigger Inspection</span>
              <v-icon>mdi-play-circle</v-icon>
            </v-btn>
            <v-progress-circular v-if="loading" indeterminate color="primary" class="ml-4"></v-progress-circular>
          </v-card-title>
          <v-card-text>
            <v-row>
              <v-col v-if="itemId" class="d-flex justify-center align-center">
                <p>Item ID: <a @click="goToItemDetail">{{ itemId }}</a></p>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <v-row v-if="snackbar">
      <v-col cols="12" class="d-flex justify-center">
        <v-alert :type="snackbarColor" :value="snackbar" dismissible @input="snackbar = false" class="snackbar-alert">
          {{ snackbarMessage }}
          <v-progress-linear v-if="snackbarColor === 'success'" :value="progress" height="4"></v-progress-linear>
        </v-alert>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import ApiService from '@/services/ApiService.js';

export default {
  name: 'TriggerView',
  data() {
    return {
      itemId: null,
      snackbar: false,
      snackbarMessage: '',
      snackbarColor: '',
      snackbarTimeout: 3000,
      progress: 0,
      loading: false
    };
  },
  methods: {
    triggerApi() {
      this.loading = true;
      ApiService.triggerApi()
        .then(response => {
          console.log('API triggered successfully:', response);
          this.itemId = response.data.item_id;
          this.snackbarMessage = 'API triggered successfully';
          this.snackbarColor = 'success';
          this.snackbar = true;
          this.dismissCountDown();
        })
        .catch(error => {
          console.error('Error triggering API:', error);
          if (!error.response) {
            this.snackbarMessage = 'Error triggering API: Backend is not available. Please start or check the backend.';
          } else {
            this.snackbarMessage = error.response.data && error.response.data.detail || 'Error triggering API';
          }
          this.snackbarColor = 'error';
          this.snackbar = true;
        })
        .finally(() => {
          this.loading = false;
        });
    },
    dismissCountDown() {
      this.progress = 100;
      const interval = 100; // Update every 100ms
      const decrement = 100 / (this.snackbarTimeout / interval);
      const timer = setInterval(() => {
        this.progress -= decrement;
        if (this.progress <= 0) {
          clearInterval(timer);
          this.snackbar = false;
        }
      }, interval);
    },
    goToItemDetail() {
      this.$router.push({ name: 'ItemDetailView', params: { id: this.itemId } });
    }
  }
};
</script>

<style scoped>
.trigger-button {
  border: 2px solid transparent;
  transition: border-color 0.3s;
}

.trigger-button:hover {
  border-color: #1976d2;
  /* Primary color */
}

.snackbar-alert {
  max-width: 600px;
  /* Adjust the width as needed */
  width: 100%;
}
</style>