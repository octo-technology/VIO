<template>
  <v-container>
    <v-row>
      <v-col cols="12" class="d-flex justify-center">
        <v-alert v-if="error" type="error" dismissible @input="error = false" class="alert-box">
          {{ errorMessage }}
        </v-alert>
      </v-col>
    </v-row>
    <v-row v-if="items.length === 0">
      <v-col cols="12" class="d-flex justify-center">
        <v-alert type="info" class="alert-box">
          No data available
        </v-alert>
      </v-col>
    </v-row>
    <v-row v-else>
      <v-col v-for="item in items" :key="item.id" cols="12" md="3">
        <v-card @click="goToItemDetail(item.id)" class="cursor-pointer item-card">
          <v-card-title>
            <v-icon class="mr-2">mdi-package-variant</v-icon>
            {{ item.id.substring(0, 18) }}
          </v-card-title>
          <v-card-subtitle>
            <v-list dense>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Creation Date</v-list-item-title>
                  <v-list-item-subtitle>{{ item.creation_date }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Overall Decision</v-list-item-title>
                  <v-list-item-subtitle><span :class="getDecisionClass(item.decision)">{{ item.decision
                      }}</span></v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Declared cameras</v-list-item-title>
                  <v-list-item-subtitle>{{ getCameraNames(item.cameras_metadata) }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Captured images</v-list-item-title>
                  <v-list-item-subtitle>{{ getBinaryNames(item.binaries) }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>Predictions</v-list-item-title>
                  <v-list-item-subtitle>{{ getPredictionNames(item.predictions) }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
              <v-list-item>
                <v-list-item-content>
                  <v-list-item-title>State</v-list-item-title>
                  <v-list-item-subtitle>{{ item.state }}</v-list-item-subtitle>
                </v-list-item-content>
              </v-list-item>
            </v-list>
          </v-card-subtitle>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import ApiService from '@/services/ApiService.js';

export default {
  name: 'AllItemsView',
  data() {
    return {
      items: [],
      error: false,
      errorMessage: ''
    };
  },
  created() {
    this.fetchItems();
  },
  methods: {
    fetchItems() {
      ApiService.getItems()
        .then(response => {
          this.items = response.data;
          this.sortItemsByCreationDate();
        })
        .catch(error => {
          console.error('Error fetching items:', error);
          const detail = error.response && error.response.data && error.response.data.detail;
          this.errorMessage = 'Error fetching items: ' + (detail || error.message || 'Unknown error');
          this.error = true;
        });
    },
    sortItemsByCreationDate() {
      this.items.sort((a, b) => new Date(b.creation_date) - new Date(a.creation_date));
    },
    goToItemDetail(itemId) {
      this.$router.push({ name: 'ItemDetailView', params: { id: itemId } });
    },
    getDecisionClass(decision) {
      switch (decision) {
        case 'OK':
          return 'decision-ok';
        case 'KO':
          return 'decision-ko';
        case 'NO_DECISION':
          return 'decision-no-decision';
        default:
          return '';
      }
    },
    getCameraNames(camerasMetadata) {
      if (camerasMetadata && typeof camerasMetadata === 'object') {
        return Object.keys(camerasMetadata).join(', ');
      }
      console.warn('camerasMetadata is not an object:', camerasMetadata);
      return '';
    },
    getBinaryNames(binaries) {
      if (binaries && typeof binaries === 'object') {
        return Object.keys(binaries).join(', ');
      }
      console.warn('binaries is not an object:', binaries);
      return '';
    },
    getPredictionNames(predictions) {
      if (predictions && typeof predictions === 'object') {
        return Object.keys(predictions).join(', ');
      }
      console.warn('predictions is not an object:', predictions);
      return '';
    }
  }
};
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}

.decision-ok {
  color: green;
}

.decision-ko {
  color: red;
}

.decision-no-decision {
  color: lightgray;
}

.alert-box {
  max-width: 600px;
  /* Adjust the width as needed */
  width: 100%;
}

.item-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.item-card:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}
</style>