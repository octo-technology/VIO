<template>
  <div>
    <div v-if="state" class="timeline">
      <ol v-for="status in Object.keys(this.statusList)" :key="status">
        <li>
          <span class="line" v-bind:class="getColor(status)"></span>
          <span>{{ status }}</span>
        </li>
      </ol>
    </div>

    <div v-if="itemId !== null">
      <p class="resultat">Item id: {{ itemId }}</p>
      <p class="decision">{{ decision }}</p>
      <div class="result" v-for="(object, index) in predictedItem" :key="index">
        <h3>{{ object.camera_id }}</h3>
        <div
          id="image-wrapper"
          :style="{ backgroundImage: `url(${object.image_url})` }"
        >
          <img :src="object.image_url" style="visibility: hidden;" />
          <div
            v-for="(inference, model_id) in object.inferences"
            :key="model_id"
          >
            <div v-for="(result, object_id) in inference" :key="object_id">
              <div v-if="'location' in result">
                <Box
                  v-bind:x-min="result['location'][0]"
                  v-bind:y-min="result['location'][1]"
                  v-bind:x-max="result['location'][2]"
                  v-bind:y-max="result['location'][3]"
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
import Box from "@/views/Box";

export default {
  name: "inference",
  components: { Box },
  props: [
    "predictedItem",
    "statusList",
    "state",
    "itemId",
    "errorMessage",
    "decision"
  ],
  methods: {
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
.result {
  display: inline-block;
  vertical-align: top;
  padding: 0 5rem 0 5rem;
}

.decision {
  font-weight: bold;
  font-size: 3rem;
}

#image-wrapper {
  background-repeat: no-repeat;
  position: relative;
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
