<template>
  <v-col cols="12">
    <v-row align="start">
      <v-col cols="12">
        <h1 class="title">Item List</h1>
      </v-col>
    </v-row>
    <v-row align="start">
      <v-col cols="12">
        <v-card tile>
          <v-simple-table>
            <template v-slot:default>
              <thead>
                <tr>
                  <th v-for="(col, index) in columns" :key="index">
                    {{ col }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="item in listItems"
                  :key="item._id"
                  @click="goToDetails(item._id)"
                >
                  <td v-for="(col, index) in columns" :key="index">
                    {{ getItemLine(item)[col] }}
                  </td>
                </tr>
              </tbody>
            </template>
          </v-simple-table>
        </v-card>
      </v-col>
    </v-row>
  </v-col>
</template>

<script>
import { mapState } from "vuex";

export default {
  name: "item-list",

  data() {
    return {
      columns: [
        "id",
        "station configuration",
        "state",
        "error",
        "received at",
        "decision"
      ]
    };
  },

  computed: mapState(["listItems"]),

  beforeMount: function() {
    this.$store.dispatch("load_items");
  },

  methods: {
    goToDetails(id) {
      this.$router.push({ name: "item-show", params: { id: id } });
    },
    getItemLine(item) {
      let itemLine = {
        id: item._id,
        "station configuration": item.station_config,
        state: item.state,
        error: item.error,
        "received at": item.received_time,
        decision: item.decision // getSensorsInferences(item)
      };
      return itemLine;
    }
  }
};
</script>

<style lang="scss" scoped>
.container {
  display: flex;
  flex-flow: row wrap;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  color: blue;
}
</style>
