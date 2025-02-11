<template>
  <v-container>
    <v-row>
      <v-col v-for="item in items" :key="item.id" cols="12" md="3">
        <v-card @click="goToItemDetail(item.id)" class="cursor-pointer">
          <v-card-title>{{ item.id }}</v-card-title>
          <v-card-subtitle>
            <p>Creation Date: {{ item.creation_date }}</p>
            <p :class="getDecisionClass(item.decision)">Overall Decision: {{ item.decision }}</p>
            <p>State: {{ item.state }}</p>
          </v-card-subtitle>
          <v-card-text>
            <div v-for="(camera, cameraId) in item.cameras_metadata" :key="cameraId">
              <h4>{{ camera.camera_id }}</h4>
              <p>Type: {{ camera.camera_type }}</p>
              <p>Position: {{ camera.position }}</p>
              <p>Model: {{ camera.model_forwarder_config.model_name }}</p>
              <p>Model Type: {{ camera.model_forwarder_config.model_type }}</p>
              <p>Resolution: {{ camera.model_forwarder_config.image_resolution.width }}x{{ camera.model_forwarder_config.image_resolution.height }}</p>
              <p>Version: {{ camera.model_forwarder_config.model_version }}</p>
              <p>Rule: {{ camera.camera_rule_config.camera_rule_type }}</p>
              <p>Decision: {{ item.camera_decisions[camera.camera_id] }}</p>
            </div>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import ApiService from '@/services/ApiService.js';

export default {
  name: 'ItemList',
  data() {
    return {
      items: [],
      showPredictions: {}
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
          this.items.forEach(item => {
            this.$set(this.showPredictions, item.id, false);
          });
        })
        .catch(error => {
          console.error('Error fetching items:', error);
        });
    },
    goToItemDetail(itemId) {
      this.$router.push({ name: 'ItemDetail', params: { id: itemId } });
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