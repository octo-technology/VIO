<template>
  <v-card elevation="5" class="mb-10 lighten-4" :color="active ? 'blue-grey darken-2' : 'dark'">
    <v-row class="no-gutters">
      <div class="col-auto">
        <div class="fill-height" :class="active && 'selected-bar'">
          &nbsp;&nbsp;&nbsp;
        </div>
      </div>
      <div class="col">
        <v-app-bar flat color="rgba(0, 0, 0, 0)">
          <v-toolbar-title class="text-h6 pl-0">
            {{ config_id }}
          </v-toolbar-title>
          <v-spacer></v-spacer>
          <v-progress-circular v-if="loading" indeterminate color="black"></v-progress-circular>
          <v-btn color="blue-grey" plain @click="toggleRawConfigurationVisibility" x>
            <v-icon>mdi-dots-vertical</v-icon>
            Details
          </v-btn>
          <v-btn color="blue-grey" plain @click="toggleEditConfigurationVisibility">
            <v-icon>mdi-square-edit-outline</v-icon>
            Edit
          </v-btn>
          <v-btn v-if="!active" color="blue-grey" dark rounded @click="changeConfiguration(config_id)">
            Activate
            <!-- fab small -->
            <v-icon>mdi-chevron-right</v-icon>
          </v-btn>
        </v-app-bar>

        <v-layout column class="px-4">
          <camera-row v-for="(camera_params, camera_id) in item_config['cameras']" :key="camera_id" :camera_id="camera_id"
            :params="camera_params" :inventory="inventory">
          </camera-row>
        </v-layout>
      </div>
    </v-row>

    <!-- <v-avatar class="ma-3" size="125" tile>
      <v-img src="https://picsum.photos/300/200"></v-img>
    </v-avatar> -->

    <v-expand-transition>
      <div>
        <div v-show="showRawConfiguration">
          <v-divider></v-divider>
          <v-card-text>
            <raw-configuration :config_id="config_id" :item_config="item_config" :inventory="inventory">
            </raw-configuration>
          </v-card-text>
        </div>

        <div v-show="showEditConfiguration">
          <v-divider></v-divider>
          <v-card-text>
            <!-- <edit-configuration></edit-configuration> -->
          </v-card-text>
        </div>
      </div>
    </v-expand-transition>
  </v-card>
</template>

<script>
import CameraRow from "./CameraRow";
import RawConfiguration from "./RawConfiguration";
// import EditConfiguration from "./EditConfiguration.vue";

export default {
  name: "configuration-card",
  components: {
    CameraRow,
    RawConfiguration,
    // EditConfiguration
  },
  props: {
    config_id: String,
    item_config: Object,
    inventory: Object,
    active: Boolean,
    loading: Boolean
  },
  data: () => ({
    showRawConfiguration: false,
    showEditConfiguration: false
  }),
  methods: {
    toggleRawConfigurationVisibility() {
      this.showRawConfiguration = !this.showRawConfiguration;
      this.showEditConfiguration = false;
    },
    toggleEditConfigurationVisibility() {
      this.showEditConfiguration = !this.showEditConfiguration;
      this.showRawConfiguration = false;
    },
    changeConfiguration(config_id) {
      this.$emit("update_configuration", config_id);
    }
  }
};
</script>

<style lang="scss" scoped>
.selected-bar {
  background-color: #607d8b;
}
</style>
