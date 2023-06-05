<template>
  <div column wrap class="px-4" :v-if="predicted_item">
    <div
      class="result"
      v-for="(camera_result, index) in predicted_item"
      :key="index"
    >
      <single-camera :camera_result="camera_result"></single-camera>
    </div>
  </div>
</template>

<script>
import SingleCamera from "./SingleCamera.vue";

export default {
  name: "multiple-cameras",
  components: { SingleCamera },
  props: {
    predicted_item: Array,
  },
  data: () => ({}),
};
</script>

<style lang="scss" scoped></style>
