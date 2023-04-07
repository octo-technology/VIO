<template>
  <div class="container">
    <h3>VIO Configuration</h3>
    <v-card
      v-for="(item_config, item_category) in configs"
      :key="item_category"
      elevation="5"
      class="config-card"
    >
      <div class="item-category">
        <input
          id="category"
          class="input-radio"
          type="radio"
          :value="item_category"
          v-model="selected_item_category"
        />
        <label for="category">{{ item_category }}</label>
      </div>
      <v-simple-table>
        <template>
          <thead>
            <tr>
              <td
                v-for="(camera_config, camera_id) in item_config['cameras']"
                :key="camera_id"
              >
                <span class="title-1">{{ camera_id }}</span>
                <div class="title-2">Settings</div>
                <div>
                  <div>Type: {{ camera_config["type"] }}</div>
                  <div>Position: {{ camera_config["position"] }}</div>
                  <div>Exposition: {{ camera_config["exposition"] }}</div>
                </div>

                <div class="title-2">Models</div>
                <div
                  v-for="(model, model_id) in camera_config['models_graph']"
                  :key="model_id"
                >
                  <span class="title-3">{{ model_id }}</span>
                  <div>Model name: {{ model["metadata"] }}</div>
                  <div>
                    Model type:
                    {{ inventory["models"][model["metadata"]]["category"] }}
                  </div>
                  <div>
                    Model version:
                    {{ inventory["models"][model["metadata"]]["version"] }}
                  </div>
                  <div>
                    Class names:
                    {{ inventory["models"][model["metadata"]]["class_names"] }}
                  </div>
                  <div>Depends on: {{ model["depends_on"] }}</div>
                </div>

                <div class="title-2">Camera Business Rule</div>
                <div class="title-3">Name</div>
                <div>{{ camera_config["camera_rule"]["name"] }}</div>
                <span class="title-3"> Parameters </span>
                <div
                  v-for="(camera_rule, camera_rule_id) in camera_config[
                    'camera_rule'
                  ]['parameters']"
                  :key="camera_rule_id"
                >
                  <span>{{ camera_rule_id }}: {{ camera_rule }}</span>
                </div>
              </td>

              <td>
                <div class="title-1">Item Business Rule</div>
                <div class="title-3">Name</div>
                <div>{{ item_config["item_rule"]["name"] }}</div>
                <span class="title-3"> Parameters </span>
                <div
                  v-for="(item_rule, item_rule_id) in item_config['item_rule'][
                    'parameters'
                  ]"
                  :key="item_rule_id"
                >
                  <span>{{ item_rule_id }}: {{ item_rule }}</span>
                </div>
              </td>
            </tr>
          </thead>
        </template>
      </v-simple-table>
    </v-card>

    <v-btn
      v-on:click="changeConfiguration(selected_item_category)"
      class="validation-button"
      >Valider
    </v-btn>
    <v-snackbar v-model="snackbar" :color="color" :timeout="timeout">
      {{ message }}
    </v-snackbar>
  </div>
</template>

<script>
import { configApiService } from "@/services";

export default {
  name: "VConfig",

  data() {
    return {
      configs: {},
      inventory: {},
      selected_item_category: "",
      snackbar: false,
      message: null,
      timeout: 1000,
      color: ""
    };
  },

  created() {
    configApiService.getConfigs().then(configs => (this.configs = configs));
    configApiService.getInventory().then(
      inventory => (this.inventory = inventory)
    );
  },
  methods: {
    changeConfiguration(item_category) {
      configApiService.setActiveConfig(item_category)
        .then(async response => {
          this.message =
            "Config " +
            JSON.parse(response.config.data)["config_name"] +
            " set";
          this.color = "green";
        })
        .catch(reason => {
          if (reason.response.status === 403) {
            console.log(reason.response.data);
            this.message = reason.response.data["message"];
            this.color = "red";
          } else {
            console.log(reason.response.data);
          }
        });
      this.snackbar = true;
    }
  }
};
</script>

<style lang="scss" scoped>
h3 {
  margin-bottom: 20px;
}

.item-category {
  margin-bottom: 10px;
}
td {
  vertical-align: top;
}

.config-card {
  padding: 10px;
  margin-bottom: 10px;
}

.validation-button {
  margin: auto;
  display: block;
}

.title-1 {
  font-weight: 600;
}

.title-2 {
  padding-top: 10px;
  font-weight: 500;
}

.input-radio {
  margin-right: 4px;
}

.title-3 {
  font-weight: 420;
}
</style>
