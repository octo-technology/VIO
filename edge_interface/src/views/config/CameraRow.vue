<template>
  <div>
    <v-divider></v-divider>
    <v-flex class="my-2">
      <v-layout row>
        <v-col md="2">
          <h4>{{ camera_id }}</h4>
          <div>Position: {{ params.position }}</div>
          <div>
            <v-chip label color="blue-grey">{{ params.type }}</v-chip>
          </div>
        </v-col>
        <v-col>
          <h4>Models</h4>
          <models-list :models_graph="params.models_graph" :inventory="inventory">
          </models-list>
        </v-col>
        <v-col md="2">
          <h4>Camera Rule</h4>
          <div>{{ params.camera_rule.name }}</div>
          <div><strong> Parameters </strong></div>
          <div v-for="(camera_rule, camera_rule_id) in params.camera_rule
            .parameters" :key="camera_rule_id">
            <span>{{ camera_rule_id }}: {{ camera_rule }}</span>
          </div>
        </v-col>
      </v-layout>
    </v-flex>
  </div>
</template>

<script>
import ModelsList from "./ModelsList.vue";

export default {
  name: "camera-row",
  components: { ModelsList },
  props: {
    camera_id: String,
    params: Object,
    inventory: Object,
  },
  data: () => ({}),
};
</script>
