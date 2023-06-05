<template>
  <v-col cols="12">
    <v-row align="start">
      <v-col>
        <h1 class="title">Item List</h1>
      </v-col>
      <v-col class="text-right">
        <router-link to="/item-gallery"><v-btn text><v-icon>mdi-view-module</v-icon>Gallery View</v-btn></router-link>
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
                <tr v-for="item in listItems" :key="item.id" @click="goToDetails(item.id)">
                  <td v-for="(col, index) in columns" :key="index">
                    
                    <span v-if="col != 'count boxes'">{{ getItemLine(item)[col] }}</span>

                    <v-chip v-if="col == 'count boxes'" :color="(getItemLine(item)[col] > 0) ? 'red' : 'grey'">{{ getItemLine(item)[col] }}</v-chip>

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
  computed: mapState(["listItems"]),

  beforeMount: function () {
    this.$store.dispatch("load_items");
  },

  data() {
    return {
      columns: [
        // "id",
        "received at",
        "station configuration",
        "state",
        "count boxes",
        // "error",
        "decision"
      ]
    };
  },

  methods: {
    goToDetails(id) {
      this.$router.push({ name: "item-show", params: { id: id } });
    },
    getItemLine(item) {
      let itemLine = {
        "id": item.id,
        "station configuration": item.station_config,
        "state": item.state,
        "error": item.error,
        "count boxes": (item.predictedItems[0]) ? item.predictedItems[0].count_boxes : 0,
        "received at": item.received_time,
        "decision": item.decision
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
