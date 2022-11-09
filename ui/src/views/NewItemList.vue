<template>
  <div class="container">
    <ul v-for="item in listItems" :key="item._id">
      <li class="card">
        <router-link :to="{ name: 'item-show', params: { id: item._id } }">
          <card v-bind:item="item"></card>
        </router-link>
      </li>
    </ul>
  </div>
</template>

<script>
import { mapState } from "vuex";
import Card from "@/components/Card";

export default {
  name: "item-list",
  components: {
    Card
  },

  data() {
    return {
      columns: ["_id", "internals", "decision"]
    };
  },

  computed: mapState(["listItems"]),

  beforeMount: function() {
    this.$store.dispatch("load_items");
  },

  methods: {
    goToDetails(id) {
      this.$router.push({ name: "item-show", params: { id: id } });
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
