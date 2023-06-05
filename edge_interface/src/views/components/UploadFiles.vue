<template>
  <div>
    <v-file-input v-model="inputs" accept=".json" label="inputs" />
    <v-file-input v-model="sensors" accept=".json" label="sensors" />
    <v-file-input
      v-model="binaries"
      accept="image/png, image/jpeg, image/bmp"
      label="binaries"
      prepend-icon="mdi-camera"
      multiple
    />

    <v-btn color="blue-grey" class="ma-2 white--text" @click="upload">
      Upload
      <v-icon right dark>
        mdi-cloud-upload
      </v-icon>
    </v-btn>

    <v-btn color="blue" class="ma-2 white--text" :disabled="isDisabled" @click="uploadNew">
      <v-icon left dark>
        mdi-refresh
      </v-icon>
      Upload new item
    </v-btn>

    <v-btn v-if="itemId != ''" type="success" color="blue-grey" class="ma-2 white--text" @click="goToDetails(itemId)">
      <v-icon left dark>
        mdi-google-analytics
      </v-icon>
      Result page for item: {{ itemId }}
    </v-btn>

    <v-alert v-if="error != ''" type="error">
      {{ error }}
    </v-alert>
  </div>
</template>

<script>
import UploadService from '@/services/UploadFilesService'

export default {
  name: 'UploadFiles',
  data() {
    return {
      inputs: null,
      sensors: null,
      binaries: null,
      itemId: '',
      error: '',
      fileInfos: []
    }
  },
  computed: {
    isDisabled() {
      return this.itemId === ''
    }
  },
  methods: {
    selectFile() {
      this.inputs = this.$refs.inputs.files.item(0)
      this.sensors = this.$refs.sensors.files.item(0)
      this.binaries = this.$refs.binaries.files
    },

    upload() {
      UploadService.upload(this.inputs, this.sensors, this.binaries).then(response => {
        this.itemId = response.data
        if ('item_id' in response.data) {
          this.itemId = response.data.item_id
        } else {
          this.error = response.data
        }
      })
    },

    uploadNew() {
      this.inputs = null
      this.sensors = null
      this.binaries = null
      this.itemId = ''
      this.error = ''
      this.fileInfos = []
    },

    goToDetails(id) {
      this.$router.push({ name: 'item-show', params: { id } })
    }
  }
}
</script>
