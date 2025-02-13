<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-alert v-if="error" type="error" dismissible @input="error = false">
          {{ errorMessage }}
        </v-alert>
      </v-col>
    </v-row>
    <v-row v-if="items.length === 0">
      <v-col cols="12">
        <v-alert type="info">
          No data available
        </v-alert>
      </v-col>
    </v-row>
    <v-row v-else>
      <v-col v-for="item in items" :key="item.id" cols="12" md="8">
        <v-card>
          <v-card-title @click="goToItemDetail(item.id)" class="cursor-pointer">{{ item.id }}</v-card-title>
          <v-card-subtitle>
            <p>Creation Date: {{ item.creation_date }}</p>
            <p :class="getDecisionClass(item.decision)">Overall Decision: {{ item.decision }}</p>
            <p>State: {{ item.state }}</p>
          </v-card-subtitle>
          <v-card-text>
            <v-row>
              <v-col v-for="(camera, cameraId) in getVisibleCameras(item)" :key="cameraId" cols="12" md="6">
                <h4>{{ camera.camera_id }}</h4>
                <p>Type: {{ camera.camera_type }}</p>
                <p>Position: {{ camera.position }}</p>
                <p>Model: {{ camera.model_forwarder_config.model_name }}</p>
                <p>Model Type: {{ camera.model_forwarder_config.model_type }}</p>
                <p>Resolution: {{ camera.model_forwarder_config.expected_image_resolution.width }}x{{ camera.model_forwarder_config.expected_image_resolution.height }}</p>
                <p>Version: {{ camera.model_forwarder_config.model_version }}</p>
                <p>Rule: {{ camera.camera_rule_config.camera_rule_type }}</p>
                <p>Decision: {{ item.camera_decisions[camera.camera_id] }}</p>
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
  name: 'AllItems',
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
    getVisibleCameras(item) {
      const camerasArray = Object.values(item.cameras_metadata);
      return camerasArray.slice(0, 2);
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
</style>