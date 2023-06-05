<template>
  <div text-center>
    <h3>Camera: {{ camera_result.camera_id }}</h3>
    <image-with-boxes :camera="camera_result"></image-with-boxes>

  </div>
</template>

<script>
import ImageWithBoxes from '../components/ImageWithBoxes.vue';

export default {
  name: "single-camera",
  components: { ImageWithBoxes },
  props: {
    camera_result: Object,
  },
};
</script>
