<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>Trigger API</v-card-title>
          <v-card-text>
            <v-row>
              <v-col>
                <v-btn @click="triggerApi">Trigger</v-btn>
              </v-col>
              <v-col v-if="itemId">
                <p>Item ID: <a @click="goToItemDetail">{{ itemId }}</a></p>
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
    <v-row v-if="snackbar">
      <v-col cols="12">
        <v-alert :type="snackbarColor" :value="snackbar" dismissible @input="snackbar = false">
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
      progress: 0
    };
  },
  methods: {
    triggerApi() {
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
          this.snackbarMessage = error.response && error.response.data && error.response.data.detail || 'Error triggering API';
          this.snackbarColor = 'error';
          this.snackbar = true;
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
/* Add any necessary styles here */
</style>