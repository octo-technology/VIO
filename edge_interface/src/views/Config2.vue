<template>
  <div class="container">
    <h2>Active Configuration</h2>

    <configuration-card
      :config_id="active_config_name"
      :item_config="active_config"
      :inventory="inventory"
      :active="true"
      :loading="active_config_loading"
    >
    </configuration-card>

    <h2>Activate another configuration</h2>
    <v-tabs class="mb-4">
      <v-tab key="all" @click="filterUseCases(null)">All</v-tab>
      <v-tab
        v-for="use_case in use_cases"
        :key="use_case"
        @click="filterUseCases(use_case)"
      >
        {{ use_case }}
      </v-tab>
    </v-tabs>

    <configuration-card
      v-for="(item_config, config_name) in filtered_configs"
      :key="config_name"
      :config_id="config_name"
      :item_config="item_config"
      :inventory="inventory"
      :active="false"
      v-on:update_configuration="requestConfigurationChange(config_name)"
    >
    </configuration-card>
  </div>
</template>

<script>
import ConfigService from "@/services/ConfigService";
import ConfigurationCard from "@/views/config/ConfigurationCard.vue";

export default {
  name: "config",
  components: { ConfigurationCard },
  data: () => ({
    use_cases: [],
    selected_use_case: String | null,
    configs: {},
    inventory: {},
    active_config: {},
    selected_item_category: "",
    active_config_loading: false,
  }),

  async created() {
    // Load inventory before the other API (to avoid key errors)
    await ConfigService.get_inventory().then(
      (response) => (this.inventory = response.data)
    );

    // Load other services
    ConfigService.get_configs().then((response) => {
      // TODO: workaround for sorting configuration in alpha order => add an "order" field in "api/v1/configs"
      let unordered_config = response.data;
      let ordered_configs = Object.keys(unordered_config)
        .sort()
        .reduce((obj, key) => {
          obj[key] = response.data[key];
          return obj;
        }, {});

      this.configs = ordered_configs;

      // TODO: workaround to create categories of config (or use cases) => It takes the characters before the "_" in the full config ID
      let build_categories = Object.keys(this.configs).map(
        (config_id) => config_id.split("_")[0]
      );
      this.use_cases = [...new Set(build_categories)].sort(); // de-deduplicate
    });

    ConfigService.get_active_config().then(
      (response) => (this.active_config = response.data)
    );
  },
  methods: {
    async requestConfigurationChange(item_category) {
      this.active_config_loading = true;
      this.active_config = this.configs[item_category];

      await ConfigService.set_active_config(item_category);
      await ConfigService.get_active_config().then(
        (response) => (this.active_config = response.data)
      );
      this.active_config_loading = false;
    },
    filterUseCases(use_case) {
      this.selected_use_case = use_case;
    },
  },
  computed: {
    // Filter configuration to display based on use case selected
    filtered_configs() {
      let filtered_configs = {};
      if (this.configs) {
        filtered_configs = Object.keys(this.configs)
          .filter(
            (key) =>
              !this.selected_use_case ||
              key.startsWith(this.selected_use_case + "_")
          )
          .reduce((obj, key) => {
            obj[key] = this.configs[key];
            return obj;
          }, {});
      }
      return filtered_configs;
    },

    // TODO: workaround to get active config name, as it is not exported in route "api/v1/configs/active"
    active_config_name() {
      let name = "";
      if (this.configs) {
        Object.keys(this.configs).forEach((config_name) => {
          if (
            JSON.stringify(this.configs[config_name]) ==
            JSON.stringify(this.active_config)
          ) {
            name = config_name;
          }
        });
      }
      return name;
    },
  },
};
</script>

<style lang="scss" scoped>
h2 {
  margin-top: 1em;
  margin-bottom: 0.5em;
}
.config-card {
  padding: 10px;
  margin-bottom: 10px;
}
</style>
