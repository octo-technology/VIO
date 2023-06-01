<template>
  <div class="mr-4 container">
    <v-btn color="blue-grey" class="ma-2 white--text" @click="trigger">
      Trigger
      <v-icon right dark>
        mdi-cloud-upload
      </v-icon>
    </v-btn>

    <div v-if="state" class="timeline">
      <ol v-for="status in Object.keys(this.statusList)" :key="status">
        <li>
          <span class="line" :class="getColor(status)" />
          <span>{{ status }}</span>
        </li>
      </ol>
    </div>

    <div v-if="itemId !== null">
      <p>Item id: {{ itemId }}</p>
      <p class="decision">
        {{ decision }}
      </p>
      <div v-for="(object, index) in predictedItem" :key="index">
        <h3>{{ object.cameraId }}</h3>
        <div>
          <img class="img-responsive" :src="object.image_url" />
          <div v-for="(inference, model_id) in object.inferences" :key="model_id">
            <div v-for="(result, object_id) in inference" :key="object_id">
              <div v-if="'location' in result">
                <Box
                  :x-min="result['location'][0]"
                  :y-min="result['location'][1]"
                  :x-max="result['location'][2]"
                  :y-max="result['location'][3]"
                />
              </div>
            </div>
          </div>
        </div>
        <div v-for="(inference, model_id) in object.inferences" :key="model_id">
          <h4>{{ model_id }}</h4>
          <div v-for="(result, object_id) in inference" :key="object_id">
            <span>{{ object_id }}</span>
            <div v-for="(value, key) in result" :key="key">
              <span>{{ key }}: {{ value }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Box from '@/views/Box'
import ItemsService from '@/services/ItemsService'
import TriggerCaptureService from '@/services/TriggerCaptureService'
import { baseURL } from '@/services/api'
import UploadService from '@/services/UploadCameraService'

export default {
  name: 'Inference',
  components: { Box },
  props: ['errorMessage', 'image'],
  data: () => ({
    predictedItem: {},
    itemId: null,
    statusList: null,
    state: undefined,
    decision: undefined
  }),
  methods: {
    getColor(status) {
      if (this.statusList[status] > this.statusList[this.state]) {
        return 'red'
      }
      return 'green'
    },
    async waitForStateDone() {
      const maxAttempts = 20
      let attempts = 0
      this.statusList = {
        Capture: 0,
        'Save Binaries': 1,
        Inference: 2,
        Decision: 3,
        Done: 4
      }
      const executePoll = async (resolve, reject) => { // eslint-disable-line
        const result = await ItemsService.getItemStateById(this.itemId)
        this.state = result.data
        attempts++

        if (this.state === 'Done') {
          return resolve(result)
        }
        if (attempts === maxAttempts) {
          return reject(new Error("L'inférence n'a pas pu être réalisée"))
        }
        setTimeout(executePoll, 800, resolve, reject)
      }

      return new Promise(executePoll)
    },
    async trigger() {
      this.predictedItem = []
      const trigger = this.image !== undefined ? UploadService.inference(this.image) : TriggerCaptureService.trigger()
      trigger
        .then(async response => {
          this.itemId = response.data.item_id
          this.$emit('update-error-message', null)

          await this.waitForStateDone()
          const itemResponse = await ItemsService.getItemById(this.itemId)
          const item = itemResponse.data
          this.decision = item.decision
          const { inferences } = item
          Object.keys(inferences).forEach(cameraId => {
            this.predictedItem.push({
              cameraId,
              inferences: inferences[cameraId],
              image_url: `${baseURL}/items/${this.itemId}/binaries/${cameraId}`
            })
          })
        })
        .catch(reason => {
          if (reason.response.status === 403) {
            this.$emit('update-error-message', reason.response.data.message)

            this.itemId = null
          }
        })
    }
  }
}
</script>

<style lang="scss" scoped>
.result {
  display: inline-block;
  vertical-align: top;
  padding: 0 5rem 0 5rem;
}

.container {
  text-align: center;
}

.decision {
  font-weight: bold;
  font-size: 3rem;
}

.timeline {
  padding: 1rem;
  overflow-x: hidden;
}

.img-responsive {
  max-width: 400px;
  width: 100%;
  height: auto;
}

ol {
  margin-bottom: 5px;
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
  content: '';
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
