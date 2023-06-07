<template>
  <div class="container">
    <h1 class="title">
      History
    </h1>
    <v-data-table :headers="columns" :items="listItems" :items-per-page="10" @click:row="goToDetails" />
    <div>
      <v-btn color="blue-grey" class="ma-2 white--text" to="/upload-camera">
        Acquisition from webcam
      </v-btn>
      <v-btn color="blue-grey" class="ma-2 white--text" to="/trigger">
        Acquisition from specific camera
      </v-btn>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'ItemList',

  data() {
    return {
      columns: [
        { text: 'Acquisition Id', value: 'id' },
        { text: 'Configuration', value: 'station_config' },
        { text: 'Status', value: 'state' },
        { text: 'Error', value: 'error' },
        { text: 'Reception Timestamp', value: 'received_time' },
        { text: 'Decision', value: 'decision' }
      ]
    }
  },

  computed: mapState(['listItems']),

  beforeMount() {
    this.$store.dispatch('load_items')
  },

  methods: {
    goToDetails(item) {
      this.$router.push({ name: 'item-show', params: { id: item.id } })
    }
  }
}
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
