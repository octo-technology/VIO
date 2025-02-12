<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title>
            <v-select
              v-model="selectedItemId"
              :items="itemIds"
              label="Select Item ID"
              @change="fetchItem"
            ></v-select>
          </v-card-title>
          <v-card-subtitle v-if="item.id">
            <p>Creation Date: {{ item.creation_date }}</p>
            <p :class="getDecisionClass(item.decision)">Overall Decision: {{ item.decision }}</p>
            <p>State: {{ item.state }}</p>
          </v-card-subtitle>
          <v-card-text v-if="item.id">
            <v-row>
              <v-col v-for="(camera, cameraId) in item.cameras_metadata" :key="cameraId" cols="6">
                <v-card>
                  <v-card-title>{{ camera.camera_id }}</v-card-title>
                  <v-card-subtitle>
                    <p>Type: {{ camera.camera_type }}</p>
                    <p>Position: {{ camera.position }}</p>
                    <p>Model: {{ camera.model_forwarder_config.model_name }}</p>
                    <p>Model Type: {{ camera.model_forwarder_config.model_type }}</p>
                    <p>Resolution: {{ camera.model_forwarder_config.expected_image_resolution.width }}x{{ camera.model_forwarder_config.expected_image_resolution.height }}</p>
                    <p>Version: {{ camera.model_forwarder_config.model_version }}</p>
                    <p>Rule: {{ camera.camera_rule_config.camera_rule_type }}</p>
                    <p>Decision: {{ item.camera_decisions[camera.camera_id] }}</p>
                  </v-card-subtitle>
                  <v-card-text>
                    <div class="image-container">
                      <v-img :src="getImageUrl(item.id, camera.camera_id)" class="image"></v-img>
                      <div v-if="camera.model_forwarder_config.model_type === 'classification'" class="overlay">
                        <p class="classification-label">{{ item.predictions[cameraId].label }}</p>
                      </div>
                      <div v-if="camera.model_forwarder_config.model_type === 'object_detection'" class="overlay">
                        <div v-for="(object, objectId) in item.predictions[cameraId].detected_objects" :key="objectId" class="bounding-box" :style="getBoundingBoxStyle(object.location)">
                          <p class="bounding-box-label">{{ object.label }}</p>
                        </div>
                      </div>
                    </div>
                  </v-card-text>
                </v-card>
              </v-col>
            </v-row>
            <div>
              <h4 @click="togglePredictions(item.id)">Predictions</h4>
              <div v-if="showPredictions[item.id]">
                <div v-for="(prediction, cameraId) in item.predictions" :key="cameraId">
                  <h5>Camera {{ cameraId }}</h5>
                  <div v-if="prediction.prediction_type === 'class'">
                    <p>Label: {{ prediction.label }}</p>
                    <p>Probability: {{ prediction.probability }}</p>
                  </div>
                  <div v-if="prediction.prediction_type === 'objects'">
                    <div v-for="(object, objectId) in prediction.detected_objects" :key="objectId">
                      <p>Location: {{ object.location }}</p>
                      <p>Objectness: {{ object.objectness }}</p>
                      <p>Label: {{ object.label }}</p>
                    </div>
                  </div>
                </div>
              </div>
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
  name: 'ItemDetail',
  data() {
    return {
      item: {},
      itemIds: [],
      selectedItemId: null,
      showPredictions: {}
    };
  },
  created() {
    this.fetchItemIds();
    const itemId = this.$route.params.id;
    if (itemId) {
      this.selectedItemId = itemId;
      this.fetchItem();
    }
  },
  watch: {
    '$route.params.id': function(newId) {
      if (newId) {
        this.selectedItemId = newId;
        this.fetchItem();
      } else {
        this.item = {};
        this.selectedItemId = null;
      }
    }
  },
  methods: {
    fetchItemIds() {
      ApiService.getItems()
        .then(response => {
          // Sort items by creation date
          const sortedItems = response.data.sort((a, b) => new Date(a.creation_date) - new Date(b.creation_date));
          this.itemIds = sortedItems.map(item => item.id);
        })
        .catch(error => {
          console.error('Error fetching item IDs:', error);
        });
    },
    fetchItem() {
      if (!this.selectedItemId) return;
      ApiService.getItem(this.selectedItemId)
        .then(response => {
          this.item = response.data;
          this.$set(this.showPredictions, this.item.id, false);
        })
        .catch(error => {
          console.error('Error fetching item:', error);
        });
    },
    getImageUrl(itemId, cameraId) {
      return ApiService.getItemImage(itemId, cameraId);
    },
    getBoundingBoxStyle(location) {
      const [x1, y1, x2, y2] = location;
      return {
        left: `${x1 * 100}%`,
        top: `${y1 * 100}%`,
        width: `${(x2 - x1) * 100}%`,
        height: `${(y2 - y1) * 100}%`
      };
    },
    togglePredictions(itemId) {
      this.$set(this.showPredictions, itemId, !this.showPredictions[itemId]);
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
.image-container {
  position: relative;
}

.image {
  width: 100%;
  height: auto;
  margin-top: 10px;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
}

.classification-label {
  position: absolute;
  top: 10px;
  left: 10px;
  background-color: rgba(255, 255, 255, 0.7);
  padding: 5px;
  border-radius: 3px;
}

.bounding-box {
  position: absolute;
  border: 2px solid red;
}

.bounding-box-label {
  position: absolute;
  top: -20px;
  left: 0;
  background-color: rgba(255, 255, 255, 0.7);
  padding: 2px 5px;
  border-radius: 3px;
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