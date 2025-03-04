<template>
  <v-card>
    <v-card-title><v-icon class="mr-2">mdi-package-variant</v-icon>{{ item.id }}</v-card-title>
    <v-card-subtitle>
      <v-row dense>
        <v-col cols="4">
          <v-list-item>
            <v-list-item-content>
              <v-list-item-title>Creation Date</v-list-item-title>
              <v-list-item-subtitle>{{ item.creation_date }}</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </v-col>
        <v-col cols="4">
          <v-list-item>
            <v-list-item-content>
              <v-list-item-title>Overall Decision</v-list-item-title>
              <v-list-item-subtitle><span :class="getDecisionClass(item.decision)">{{ item.decision }}</span></v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </v-col>
        <v-col cols="4">
          <v-list-item>
            <v-list-item-content>
              <v-list-item-title>State</v-list-item-title>
              <v-list-item-subtitle>{{ item.state }}</v-list-item-subtitle>
            </v-list-item-content>
          </v-list-item>
        </v-col>
      </v-row>
    </v-card-subtitle>
    <v-card-text>
      <v-row class="reduced-spacing">
        <v-col v-for="(camera, cameraId) in item.cameras_metadata" :key="cameraId" cols="6">
          <v-card>
            <v-card-title><v-icon class="mr-2">mdi-camera</v-icon>Camera details: {{ camera.camera_id }}</v-card-title>
            <v-card-subtitle>
              <v-list dense>
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title>Type</v-list-item-title>
                    <v-list-item-subtitle>{{ camera.camera_type }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item v-if="camera.source_directory">
                  <v-list-item-content>
                    <v-list-item-title>Source Directory</v-list-item-title>
                    <v-list-item-subtitle>{{ camera.source_directory }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item>
                  <v-list-item-content>
                    <v-list-item-title>Position</v-list-item-title>
                    <v-list-item-subtitle>{{ camera.position }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item v-if="camera.camera_resolution">
                  <v-list-item-content>
                    <v-list-item-title>Resolution</v-list-item-title>
                    <v-list-item-subtitle>{{ camera.camera_resolution.width }}x{{ camera.camera_resolution.height }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
              <div>
                <h4>Model Details</h4>
                <v-list dense>
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-title>Model Name</v-list-item-title>
                      <v-list-item-subtitle>{{ camera.model_forwarder_config.model_name }}</v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-title>Model Type</v-list-item-title>
                      <v-list-item-subtitle>{{ camera.model_forwarder_config.model_type }}</v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                  <v-list-item v-if="camera.model_forwarder_config.expected_image_resolution">
                    <v-list-item-content>
                      <v-list-item-title>Expected Image Resolution</v-list-item-title>
                      <v-list-item-subtitle>{{ camera.model_forwarder_config.expected_image_resolution.width }}x{{ camera.model_forwarder_config.expected_image_resolution.height }}</v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-title>Version</v-list-item-title>
                      <v-list-item-subtitle>{{ camera.model_forwarder_config.model_version }}</v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                  <v-list-item>
                    <v-list-item-content>
                      <v-list-item-title>Model Serving URL</v-list-item-title>
                      <v-list-item-subtitle><a :href="camera.model_forwarder_config.model_serving_url" target="_blank">{{ camera.model_forwarder_config.model_serving_url }}</a></v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                </v-list>
              </div>
              <v-list dense>
                <v-list-item v-if="camera.camera_rule_config">
                  <v-list-item-content>
                    <v-list-item-title>Rule</v-list-item-title>
                    <v-list-item-subtitle>{{ camera.camera_rule_config.camera_rule_type }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item v-if="camera.camera_rule_config.expected_class">
                  <v-list-item-content>
                    <v-list-item-title>Expected Class</v-list-item-title>
                    <v-list-item-subtitle>{{ camera.camera_rule_config.expected_class }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item v-if="camera.camera_rule_config.unexpected_class">
                  <v-list-item-content>
                    <v-list-item-title>Unexpected Class</v-list-item-title>
                    <v-list-item-subtitle>{{ camera.camera_rule_config.unexpected_class }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item v-if="camera.camera_rule_config.class_to_detect">
                  <v-list-item-content>
                    <v-list-item-title>Class to Detect</v-list-item-title>
                    <v-list-item-subtitle>{{ camera.camera_rule_config.class_to_detect }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item v-if="camera.camera_rule_config.threshold">
                  <v-list-item-content>
                    <v-list-item-title>Threshold</v-list-item-title>
                    <v-list-item-subtitle>{{ camera.camera_rule_config.threshold }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                <v-list-item v-if="item.camera_decisions && item.camera_decisions[camera.camera_id]">
                  <v-list-item-content>
                    <v-list-item-title>Decision</v-list-item-title>
                    <v-list-item-subtitle>{{ item.camera_decisions[camera.camera_id] }}</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
              <div>
                <h4 @click="togglePredictions(cameraId)">
                  Predictions
                  <v-icon>{{ showPredictions[cameraId] ? 'mdi-eye-off' : 'mdi-eye' }}</v-icon>
                </h4>
                <v-list dense v-if="showPredictions[cameraId]">
                  <v-list-item v-if="item.predictions && item.predictions[cameraId]">
                    <v-list-item-content>
                      <v-list-item-title>Label</v-list-item-title>
                      <v-list-item-subtitle>{{ item.predictions[cameraId].label }}</v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                  <v-list-item v-if="item.predictions && item.predictions[cameraId]">
                    <v-list-item-content>
                      <v-list-item-title>Probability</v-list-item-title>
                      <v-list-item-subtitle>{{ item.predictions[cameraId].probability }}</v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                  <v-list-item v-if="item.predictions && item.predictions[cameraId] && item.predictions[cameraId].prediction_type === 'objects'">
                    <v-list-item-content>
                      <v-list-item-title>Detected Objects</v-list-item-title>
                      <v-list-item-subtitle>
                        <v-list dense>
                          <v-list-item v-for="(object, objectId) in item.predictions[cameraId].detected_objects" :key="objectId">
                            <v-list-item-content>
                              <v-list-item-title>Location</v-list-item-title>
                              <v-list-item-subtitle>{{ object.location }}</v-list-item-subtitle>
                            </v-list-item-content>
                          </v-list-item>
                          <v-list-item>
                            <v-list-item-content>
                              <v-list-item-title>Objectness</v-list-item-title>
                              <v-list-item-subtitle>{{ object.objectness }}</v-list-item-subtitle>
                            </v-list-item-content>
                          </v-list-item>
                          <v-list-item>
                            <v-list-item-content>
                              <v-list-item-title>Label</v-list-item-title>
                              <v-list-item-subtitle>{{ object.label }}</v-list-item-subtitle>
                            </v-list-item-content>
                          </v-list-item>
                        </v-list>
                      </v-list-item-subtitle>
                    </v-list-item-content>
                  </v-list-item>
                  <v-list-item v-if="!item.predictions || !item.predictions[cameraId]">
                    <v-list-item-content>
                      <v-list-item-title>No Predictions Available</v-list-item-title>
                    </v-list-item-content>
                  </v-list-item>
                </v-list>
              </div>
            </v-card-subtitle>
            <v-card-text>
              <div class="image-container">
                <v-img :src="getImageUrl(item.id, camera.camera_id)" class="image"></v-img>
                <div v-if="camera.model_forwarder_config.model_type === 'classification'" class="overlay">
                  <p class="classification-label" v-if="item.predictions && item.predictions[cameraId] && item.predictions[cameraId].label">{{ item.predictions[cameraId].label }}</p>
                </div>
                <div v-if="camera.model_forwarder_config.model_type === 'object_detection'" class="overlay">
                  <div v-for="(object, objectId) in item.predictions && item.predictions[cameraId]?.detected_objects" :key="objectId" class="bounding-box" :style="getBoundingBoxStyle(object.location)">
                    <p class="bounding-box-label">{{ object.label }}</p>
                  </div>
                </div>
              </div>
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-card-text>
  </v-card>
</template>

<script>
import ApiService from '@/services/ApiService.js';

export default {
  name: 'ItemDetails',
  props: {
    item: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      showPredictions: {}
    };
  },
  methods: {
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
    togglePredictions(cameraId) {
      this.$set(this.showPredictions, cameraId, !this.showPredictions[cameraId]);
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
.centered {
  display: flex;
  justify-content: center;
}

.max-width-500 {
  max-width: 500px;
}

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
  right: 10px;
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

.reduced-spacing .v-row {
  margin-bottom: 8px; /* Adjust this value to reduce the space between rows */
}
</style>