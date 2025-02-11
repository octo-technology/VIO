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
  </v-container>
</template>

<script>
import ApiService from '@/services/ApiService.js';

export default {
  name: 'TriggerView',
  data() {
    return {
      itemId: null
    };
  },
  methods: {
    triggerApi() {
      ApiService.triggerApi()
        .then(response => {
          console.log('API triggered successfully:', response);
          this.itemId = response.data.item_id;
        })
        .catch(error => {
          console.error('Error triggering API:', error);
        });
    },
    goToItemDetail() {
      this.$router.push({ name: 'ItemDetail', params: { id: this.itemId } });
    }
  }
};
</script>

<style scoped>
/* Add any necessary styles here */
</style>