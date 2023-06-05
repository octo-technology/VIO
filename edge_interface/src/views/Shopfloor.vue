<template>
  <v-container fluid>
    <v-layout column text-center>
      <div v-if="error_message" class="no_configuration">
        <v-alert color="red" dismissible elevation="10" type="warning">
          {{ this.error_message }}
        </v-alert>
      </div>

      <timeline :state="state"></timeline>

      <v-layout row wrap class="my-10">
        <v-flex xs4 class="pr-3">
          <div class="my-4">
            <v-btn class="ma-2 white--text" color="blue-grey" id="trigger-button" :loading="pictureAcquisition"
              :disabled="pictureAcquisition || url_item_id != null" @click="trigger">
              <v-icon class="camera">mdi-camera</v-icon>
            </v-btn>
          </div>

          <div class="my-4">
            <div>
              <!-- v-if="item_id" -->
              <p class="resultat">
                Item id:
                <a :href="get_item_URL(item_id)" target="_blank">
                  {{ item_id }}
                </a>
              </p>
              <p class="decision">{{ decision }}</p>
            </div>
          </div>

          <div class="my-4" :v-if="item">
            <model-results-table :item="item"></model-results-table>
          </div>
        </v-flex>

        <v-flex>
          <multiple-cameras :predicted_item="predicted_item"></multiple-cameras>
        </v-flex>
      </v-layout>
    </v-layout>
  </v-container>
</template>

<script>
import TriggerCaptureService from "@/services/TriggerCaptureService";
import ItemsService from "@/services/ItemsService";
import { baseURL } from "@/services/api";
import ModelResultsTable from "./shopfloor/ModelResultsTable";
import MultipleCameras from "./shopfloor/MultipleCameras.vue";
import Timeline from "./shopfloor/Timeline.vue";

export default {
  name: "ShopfloorUI",
  components: {
    ModelResultsTable,
    MultipleCameras,
    Timeline,
  },
  props: {
    url_item_id: String,
  },

  data() {
    return {
      item: null,
      predicted_item: [],
      state: "",
      item_id: null,
      error_message: null,
      decision: undefined,
      pictureAcquisition: false,
      attempts: 0
    };
  },

  async created() {
    if (this.url_item_id) {
      console.log("Fetch item in history");
      this.item_id = this.url_item_id;
      await this.fetchItem(this.url_item_id); // fetch item if provided in URL
    }
  },

  methods: {
    get_item_URL(item_id) {
      return baseURL + "/items/" + item_id;
    },
    async trigger() {

      this.pictureAcquisition = true;
      this.item = null;
      this.item_id = "";
      this.predicted_item = [];
      this.decision = "";
      this.state = null;

      TriggerCaptureService.trigger()
        .then(async (response) => {
          this.item_id = response.data["item_id"];
          this.error_message = null;



          await this.waitForStateDone();
          await this.fetchItem(this.item_id);

          this.pictureAcquisition = false;
        })
        .catch((reason) => {
          if (reason.response.status === 403) {
            this.error_message = reason.response.data["message"];
            this.item_id = null;
          } else {
            console.log(reason.response.data);
          }
        });
    },

    async waitForStateDone() {
      const maxAttempts = 100;
      this.attempts = 0;
      const executePoll = async (resolve, reject) => {
        const result = await ItemsService.get_item_state_by_id(this.item_id);
        this.state = result.data;
        this.attempts++;

        if (this.state === "Done") {
          return resolve(result);
        } else if (this.attempts === maxAttempts) {
          return reject(new Error("L'inférence n'a pas pu être réalisée"));
        } else {
          setTimeout(executePoll, 500, resolve, reject);
        }
      };

      return new Promise(executePoll);
    },

    async fetchItem(item_id) {
      this.predicted_item = [];
      const itemResponse = await ItemsService.get_item_by_id(item_id);
      const item = itemResponse.data;
      this.item = item;

      this.decision = item["decision"];
      const inferences = item["inferences"];

      Object.keys(inferences).forEach((camera_id) => {
        this.predicted_item.push({
          camera_id: camera_id,
          inferences: inferences[camera_id],
          image_url: `${baseURL}/items/${item_id}/binaries/${camera_id}`,
        });
      });

      // console.log("built predicted item", this.predicted_item);
    },
  },
};
</script>

<style lang="scss" scoped>
.result {
  display: inline-block;
  vertical-align: top;
  padding: 0 5rem 0 5rem;
}

.decision {
  font-weight: bold;
  font-size: 3rem;
}

.no_configuration {
  padding: 6rem 0;
}

#trigger-button {
  width: 15em;
  height: 12em;
}

.camera {
  font-size: 8em;
  color: white;
}
</style>
