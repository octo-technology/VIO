<template>
  <table class="models-list">
    <thead>
      <tr>
        <th class="text-left">Type</th>
        <th class="text-left">Id</th>
        <th class="text-left">Name</th>
        <th class="text-left">Classes</th>
        <th class="text-left">Depends on</th>
      </tr>
    </thead>
    <tbody>
      <tr v-for="(model_params, model_id) in models_graph" :key="model_id">
        <td>
          <strong>{{
            inventory.models[model_params.metadata]["category"]
          }}</strong>
        </td>
        <td>
          {{ model_id }}
        </td>
        <td class="model-name">
          <span class="model-name">{{ model_params.metadata }}</span>
          <v-chip class="ma-2" small outlined color="blue-grey"><strong>v
              {{ inventory.models[model_params.metadata]["version"] }}</strong></v-chip>
        </td>
        <td>
          {{ inventory.models[model_params.metadata]["class_names"] }}
        </td>
        <td>
          {{ model_params.depends_on }}
        </td>
      </tr>
    </tbody>
  </table>
</template>

<script>
export default {
  name: "models-list",
  props: {
    models_graph: Object,
    inventory: Object,
  },
  data: () => ({}),
};
</script>

<style lang="scss" scoped>
table.models-list {
  width: 90%;
}

table.models-list th {
  font-size: 0.9rem;
  padding: 0.5em 0;
}

table.models-list td {
  vertical-align: middle;
  padding: 0.5em 0;
}

.model-name {
  font-size: 0.9rem;
}
</style>
