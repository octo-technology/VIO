<template>
  <div>
    <h3>Raw configuration details</h3>
    <v-simple-table>
      <template>
        <thead>
          <tr>
            <td v-for="(camera_config, camera_id) in item_config['cameras']" :key="camera_id">
              <span class="title-1">{{ camera_id }}</span>
              <div>
                <div>Type: {{ camera_config["type"] }}</div>
                <div>Position: {{ camera_config["position"] }}</div>
              </div>

              <div class="title-2">Models</div>
              <div v-for="(model, model_id) in camera_config['models_graph']" :key="model_id">
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
              <div :v-if="camera_config.camera_rule">
                {{ camera_config["camera_rule"]["name"] }}
              </div>
              <span class="title-3"> Parameters </span>
              <div v-for="(camera_rule, camera_rule_id) in camera_config[
                'camera_rule'
              ]['parameters']" :key="camera_rule_id">
                <span>{{ camera_rule_id }}: {{ camera_rule }}</span>
              </div>
            </td>

            <td>
              <div class="title-1">Item Business Rule</div>
              <div class="title-3">Name</div>
              <div :v-if="item_config.item_rule">
                {{ item_config["item_rule"]["name"] }}
              </div>
              <span class="title-3"> Parameters </span>
              <div v-for="(item_rule, item_rule_id) in item_config['item_rule'][
                'parameters'
              ]" :key="item_rule_id">
                <span>{{ item_rule_id }}: {{ item_rule }}</span>
              </div>
            </td>
          </tr>
        </thead>
      </template>
    </v-simple-table>
  </div>
</template>

<script>
export default {
  name: "raw-configuration",
  props: {
    config_id: String,
    item_config: Object,
    inventory: Object,
  },
  data: () => ({}),
  useEffect: () => { },
};
</script>

<style lang="scss" scoped>
table {
  background-color: transparent;
}

.title-1 {
  font-weight: 600;
}

.title-2 {
  padding-top: 10px;
  font-weight: 500;
}

.title-3 {
  font-weight: 420;
}

td {
  vertical-align: top;
}
</style>
