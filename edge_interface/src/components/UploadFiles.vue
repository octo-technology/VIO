<template>
  <div>
    <v-file-input accept=".json" v-model="inputs" label="inputs"></v-file-input>
    <v-file-input
      accept=".json"
      v-model="sensors"
      label="sensors"
    ></v-file-input>
    <v-file-input
      accept="image/png, image/jpeg, image/bmp"
      v-model="binaries"
      label="binaries"
      prepend-icon="mdi-camera"
      multiple
    ></v-file-input>

    <v-btn color="blue-grey" class="ma-2 white--text" @click="upload">
      Upload
      <v-icon right dark>mdi-cloud-upload</v-icon>
    </v-btn>

    <v-btn
      color="blue"
      class="ma-2 white--text"
      @click="uploadNew"
      :disabled="isDisabled"
    >
      <v-icon left dark>mdi-refresh</v-icon>
      Upload new item
    </v-btn>

    <v-btn
      v-if="item_id != ''"
      type="success"
      color="blue-grey"
      class="ma-2 white--text"
      @click="goToDetails(item_id)"
    >
      <v-icon left dark>mdi-google-analytics</v-icon>
      Result page for item: {{ item_id }}
    </v-btn>

    <v-alert v-if="error != ''" type="error">
      {{ error }}
    </v-alert>
  </div>
</template>

<script>
import UploadService from "@/services/UploadFilesService";

export default {
  name: "upload-files",
  data() {
    return {
      inputs: null,
      sensors: null,
      binaries: null,
      item_id: "",
      error: "",
      fileInfos: []
    };
  },
  computed: {
    isDisabled() {
      return this.item_id == "";
    }
  },
  methods: {
    selectFile() {
      this.inputs = this.$refs.inputs.files.item(0);
      this.sensors = this.$refs.sensors.files.item(0);
      this.binaries = this.$refs.binaries.files;
    },

    upload() {
      UploadService.upload(this.inputs, this.sensors, this.binaries).then(
        response => {
          this.item_id = response.data;
          if ("item_id" in response.data) {
            this.item_id = response.data["item_id"];
          } else {
            this.error = response.data;
          }
        }
      );
    },

    uploadNew() {
      this.inputs = null;
      this.sensors = null;
      this.binaries = null;
      (this.item_id = ""), (this.error = ""), (this.fileInfos = []);
    },

    goToDetails(id) {
      this.$router.push({ name: "item-show", params: { id: id } });
    }
  }
};
</script>
