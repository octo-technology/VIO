<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-select
          v-model="selectedConfigs"
          :items="configOptions"
          label="Select Configs"
          multiple
          item-text="station_name"
          item-value="station_name"
        ></v-select>
      </v-col>
    </v-row>
    <v-row>
      <v-col v-for="config in filteredConfigs" :key="config.station_name" cols="12" md="6">
        <v-card>
          <v-card-title>
            {{ config.station_name }}
            <v-btn @click="setActiveConfig(config.station_name)" small color="primary" class="ml-2">Set Active</v-btn>
          </v-card-title>
          <v-card-text>
            <config-details :config="config"></config-details>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import ApiService from '@/services/ApiService.js';
import ConfigDetails from './ConfigDetails.vue';

export default {
  name: 'AllConfigsView',
  components: {
    ConfigDetails
  },
  data() {
    return {
      configs: [],
      selectedConfigs: []
    };
  },
  created() {
    this.fetchConfigs();
  },
  computed: {
    configOptions() {
      return this.configs.map(config => config.station_name);
    },
    filteredConfigs() {
      return this.configs.filter(config => this.selectedConfigs.includes(config.station_name));
    }
  },
  methods: {
    fetchConfigs() {
      ApiService.getConfigs()
        .then(response => {
          // Transform the response data to an array of configs
          this.configs = Object.values(response.data);
        })
        .catch(error => {
          console.error('Error fetching configs:', error);
          this.configs = [];
        });
    },
    setActiveConfig(stationName) {
      ApiService.setActiveConfigByName(stationName)
        .then(response => {
          console.log('Active config set successfully:', response.data);
          this.$emit('active-config-updated'); // Emit an event to notify parent component
        })
        .catch(error => {
          console.error('Error setting active config:', error);
        });
    }
  }
};
</script>

<style scoped>
/* Add any necessary styles here */
</style>