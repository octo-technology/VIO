<template>
  <div class="container">
    <h1 class="title">Acquisition history</h1>
    <v-data-table :headers="columns" :items="listItems" :items-per-page="10" @click:row="goToDetails"> </v-data-table>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'item-list',

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
