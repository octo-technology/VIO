<template>
  <v-col cols="12">
    <v-row align="start">
      <v-col>
        <h1 class="title">Item Gallery</h1>
      </v-col>
      <v-col class="text-right">
        <router-link to="/item-list"><v-btn text><v-icon>mdi-view-list</v-icon>List View</v-btn></router-link>
      </v-col>
    </v-row>

    <v-row no-gutters>
      <v-col v-for="item in listItems" :key="item.id" @click="goToDetails(item.id)">
        <div v-if="item.predictedItems.length > 0">
          <v-badge :content="item.predictedItems[0].count_boxes" :value="item.predictedItems[0].count_boxes > 0" top
            offset-x="20" offset-y="20" color="red" bordered>

            <!-- <img :src="item.predictedItems[0].image_url" class="card" width="200" /> -->
            
            <image-with-boxes :camera="item.predictedItems[0]"  class="card"></image-with-boxes>
          </v-badge>
        </div>

      </v-col>
    </v-row>
  </v-col>
</template>


<script>
import { mapState } from "vuex";
import ImageWithBoxes from './components/ImageWithBoxes.vue';

export default {
  components: { ImageWithBoxes },
  computed: mapState(["listItems"]),

  beforeMount: function () {
    this.$store.dispatch("load_items");
    console.log("items", this.listItems)
  },
  data() {
    return {
    };
  },
  methods: {
    goToDetails(id) {
      this.$router.push({ name: "item-show", params: { id: id } });
    },
  }
};
</script>

<style scoped>
.card {
  margin: 10px;
  width: 200px;
}
</style>