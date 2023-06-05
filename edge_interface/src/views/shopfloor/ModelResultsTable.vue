<template>
  <div :v-if="item">
    <v-simple-table class="mx-2">
      <template v-slot:default>
        <thead>
          <tr>
            <th v-for="(col, index) in columns" :key="index" class="text-center">
              {{ col }}
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(inference, index) in getListOfInferences" :key="index">
            <td>{{ inference["camera"] }}</td>
            <td>{{ inference["model"] }}</td>
            <td>
              {{ inference["decision"] }}
              <!-- <div v-for="(result, object_id) in inf['objects']" :key="object_id">
                <strong>{{ object_id }}</strong>
                <div v-for="(value, key) in result" :key="key">
                  <span>{{ key }}:
                    {{
                      typeof value == "number" ? value.toFixed(2) : value
                    }}</span>
                </div>
              </div> -->
            </td>
          </tr>
        </tbody>
      </template>
    </v-simple-table>
  </div>
</template>

<script>
export default {
  name: "model-results-table",
  props: ["item"],
  // props: {
  //   item: Array,
  // },
  data() {
    return {
      columns: ["camera", "model", "result"],
    };
  },

  computed: {
    getListOfInferences() {
      let results = [];

      if (this.item != null) {
        Object.entries(this.item["inferences"]).forEach(
          ([camera_id, model_runs]) => {
            Object.entries(model_runs).forEach(([model_id, objects]) => {
              // console.log(camera_id, model_id, objects);

              results.push({
                camera: camera_id,
                model: model_id,
                objects,
              });
            });
          }
        );
      }
      return results;
    },
  },
};
</script>
