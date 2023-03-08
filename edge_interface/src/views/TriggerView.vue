<template>
  <div class="container">
    <div>
      <h3>Trigger the capture of an item</h3>
      <h4>Just click on the button below, VIO will do the rest</h4>
      <v-btn color="blue-grey" class="ma-2 white--text" @click="trigger">
        Trigger
        <v-icon right dark>mdi-cloud-upload</v-icon>
      </v-btn>
    </div>

    <Inference
      :predictedItem="predictedItem"
      :statusList="statusList"
      :state="state"
      :item_id="item_id"
      :errorMessage="errorMessage"
      :decision="decision"
    />
    <div v-if="errorMessage !== null" class="no_configuration">
      <v-alert color="red" dismissible elevation="10" type="warning"
        >{{ this.errorMessage }}
      </v-alert>
    </div>
  </div>
</template>

<script>
import TriggerCaptureService from "@/services/TriggerCaptureService";
import ItemsService from "@/services/ItemsService";
import Inference from "@/components/Inference";
import { baseURL } from "@/services/api";

export default {
  name: "item-trigger",
  components: { Inference },
  data() {
    return {
      predictedItem: {},
      state: undefined,
      item_id: null,
      errorMessage: null,
      decision: undefined,
      statusList: null
    };
  },

  methods: {
    async waitForStateDone() {
      const maxAttempts = 20;
      let attempts = 0;
      this.statusList = {
        Capture: 0,
        "Save Binaries": 1,
        Inference: 2,
        Decision: 3,
        Done: 4
      };
      const executePoll = async (resolve, reject) => {
        const result = await ItemsService.get_item_state_by_id(this.item_id);
        this.state = result.data;
        attempts++;

        if (this.state === "Done") {
          return resolve(result);
        } else if (attempts === maxAttempts) {
          return reject(new Error("L'inférence n'a pas pu être réalisée"));
        } else {
          setTimeout(executePoll, 800, resolve, reject);
        }
      };

      return new Promise(executePoll);
    },
    async trigger() {
      this.predictedItem = [];
      TriggerCaptureService.trigger()
        .then(async response => {
          this.item_id = response.data["item_id"];
          this.errorMessage = null;

          await this.waitForStateDone();
          const itemResponse = await ItemsService.get_item_by_id(this.item_id);
          const item = itemResponse.data;
          this.decision = item["decision"];
          const inferences = item["inferences"];
          Object.keys(inferences).forEach(camera_id => {
            this.predictedItem.push({
              camera_id: camera_id,
              inferences: inferences[camera_id],
              image_url: `${baseURL}/items/${this.item_id}/binaries/${camera_id}`
            });
          });
        })
        .catch(reason => {
          if (reason.response.status === 403) {
            console.log(reason.response.data);
            this.errorMessage = reason.response.data["message"];
            this.item_id = null;
          } else {
            console.log(reason.response.data);
          }
        });
    },
    getColor(status) {
      if (this.statusList[status] > this.statusList[this.state]) {
        return "red";
      } else {
        return "green";
      }
    }
  }
};
</script>

<style lang="scss" scoped>
.container {
  text-align: center;
}

.result {
  display: inline-block;
  vertical-align: top;
  padding: 0 5rem 0 5rem;
}

.decision {
  font-weight: bold;
  font-size: 3rem;
}

.box {
  position: absolute;
  border: 2px #f30b0b solid;
}

#image-wrapper {
  background-repeat: no-repeat;
  position: relative;
}

.no_configuration {
  padding: 6rem 0;
}

.timeline {
  padding: 3rem;
  white-space: nowrap;
  overflow-x: hidden;
}

ol {
  display: inline-block;
  list-style: none;
}

.timeline ol li {
  position: relative;
  display: inline-block;
  list-style-type: none;
  width: 160px;
  height: 3px;
  background: #bfbfbf;
}

.line {
  content: "";
  position: absolute;
  top: 50%;
  left: calc(100% + 1px);
  bottom: 0;
  width: 12px;
  height: 12px;
  transform: translateY(-50%);
  border-radius: 50%;
}

.red {
  background: #d41928;
}

.green {
  background: #51d419;
}
</style>
