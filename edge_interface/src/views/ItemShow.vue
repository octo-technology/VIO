<template>
  <v-col cols="12">
    <v-row>
      <v-col cols="12">
        <v-btn class="ma-2" text link to="/">
          <v-icon left>
            mdi-arrow-left
          </v-icon>
          Back to Item List
        </v-btn>
        <item-card :item="loadItem" />
        <figure v-for="(image, index) in images" :key="index">
          <img :src="'data:image/png;base64,' + image" class="img-responsive" />
        </figure>
      </v-col>
    </v-row>
    <v-row>
      <v-col v-for="(sensor_id, index) in loadSensorsIdList" :key="index" :cols="3">
        <sensor-card :item="loadItem" :sensor_id="sensor_id" />
      </v-col>
    </v-row>
  </v-col>
</template>

<script>
import ItemCard from '@/components/ItemCard.vue'
import SensorCard from '@/components/SensorCard.vue'
import { getSensorsIdList } from '@/services/methods.js'
import ItemsService from '@/services/ItemsService.js'

export default {
  components: {
    ItemCard,
    SensorCard
  },
  props: ['id'],
  data: () => ({
    images: [],
    item: null,
    sensorsIdList: null
  }),
  async mounted() {
    const cameraIdList = Object.keys(this.item.cameras)
    if (cameraIdList && cameraIdList.length > 0) {
      const binariesList = await Promise.all(
        cameraIdList.map(
        async cameraId => await ItemsService.getItemBinaryForCameraById(this.id, cameraId)  // eslint-disable-line
        )
      )
      this.images = binariesList.map(binnaries => this.arrayBufferToBase64(binnaries.data))
    }
  },
  computed: {
    loadItem() {
      return this.changeItem()
    },
    loadSensorsIdList() {
      return this.changeSensorsIdList()
    }
  },
  beforeMount() {
    this.$store.dispatch('load_items')
  },
  methods: {
    back() {
      this.$router.go(-1)
    },
    arrayBufferToBase64(buffer) {
      let binary = ''
      const bytes = new Uint8Array(buffer)
      const len = bytes.byteLength
      for (let i = 0; i < len; i++) { // eslint-disable-line
        binary += String.fromCharCode(bytes[i])
      }
      return window.btoa(binary)
    },
    changeItem() {
      if (this.item == null) this.item = this.$store.getters.getItemById(this.id)
      return this.item
    },
    changeSensorsIdList() {
      if (this.sensorsIdList == null)
        this.sensorsIdList = getSensorsIdList(this.loadItem);
      return this.sensorsIdList;
      if (this.item == null) this.sensorsIdList = getSensorsIdList(this.loadItem)
      return this.sensorsIdList
    }
  }
}
</script>

<style lang="scss" scoped>
.img-responsive {
  max-width: 400px;
  width: 100%;
  height: auto;
}
</style>
