<template>
  <v-col cols="12">
    <v-row>
      <v-col cols="12">
        <v-btn class="ma-2" text link to="/">
          <v-icon left>mdi-arrow-left</v-icon> Back to Item List
        </v-btn>
        <item-card v-bind:item="loadItem"></item-card>
      </v-col>
    </v-row>
    <v-row>
      <v-col
        v-for="(sensor_id, index) in loadSensorsIdList"
        :key="index"
        :cols="3"
      >
        <sensor-card :item="loadItem" :sensor_id="sensor_id"> </sensor-card>
      </v-col>
    </v-row>
  </v-col>
</template>

<script>
import ItemCard from "@/components/ItemCard";
import SensorCard from "@/components/SensorCard";
import { getSensorsIdList } from "@/services/methods";

export default {
  components: {
    ItemCard,
    SensorCard
  },
  methods: {
    back() {
      console.log("back");
      this.$router.go(-1);
    }
  },
  props: ["id"],
  beforeMount: function() {
    this.$store.dispatch("load_items");
  },
  computed: {
    loadItem() {
      return this.$store.getters.getItemById(this.id);
    },
    loadSensorsIdList() {
      console.log(getSensorsIdList(this.loadItem));
      return getSensorsIdList(this.loadItem);
    }
  }
};
</script>

<style lang="scss" scoped></style>
