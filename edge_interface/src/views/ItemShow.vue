<template>
  <v-col cols="12">
    <v-row>
      <v-col cols="12">
        <v-btn class="ma-2" text link to="/">
          <v-icon left>mdi-arrow-left</v-icon> Back to Item List
        </v-btn>
        <item-card v-bind:item="loadItem"></item-card>
        <figure v-for="img in imgs" :key="img" v-show="img" class="mt-2 figure">
          <img :src="'data:image/png;base64,' + img" class="img-responsive" />
        </figure>
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
import ItemsService from "@/services/ItemsService";

export default {
  data: () => ({
    imgs: [],
    item: null,
    sensorsIdList: null
  }),
  components: {
    ItemCard,
    SensorCard
  },
  methods: {
    back() {
      console.log("back");
      this.$router.go(-1);
    },
    arrayBufferToBase64(buffer) {
      let binary = "";
      const bytes = new Uint8Array(buffer);
      const len = bytes.byteLength;
      for (let i = 0; i < len; i++) {
        binary += String.fromCharCode(bytes[i]);
      }
      return window.btoa(binary);
    },
    changeItem() {
      if (this.item == null)
        this.item = this.$store.getters.getItemById(this.id);
      return this.item;
    },
    changeSensorsIdList() {
      if (this.item == null)
        this.sensorsIdList = getSensorsIdList(this.loadItem);
      return this.sensorsIdList;
    }
  },
  props: ["id"],
  beforeMount: function() {
    this.$store.dispatch("load_items");
  },
  async mounted() {
    const camera_ids = Object.keys(this.item.cameras);
    camera_ids.forEach(async (camera_id) => {
       const result = await ItemsService.getItemBinaryForCameraById(this.id, camera_id);
       this.imgs.push(this.arrayBufferToBase64(result.data));
    })
  },
  computed: {
    loadItem() {
      return this.changeItem();
    },
    loadSensorsIdList() {
      return this.changeSensorsIdList();
    }
  }
};
</script>

<style lang="scss" scoped>
.img-responsive {
  max-width: 400px;
  width: 100%;
  height: auto;
}
</style>
