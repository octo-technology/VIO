<template>
  <div
    class="box"
    :style="{
      top: yMin + 'px',
      left: xMin + 'px',
      width: xMax - xMin + 'px',
      height: yMax - yMin + 'px',
    }"
  ></div>
</template>

<script>
export default {
  name: "Box",
  props: {
    "x-min": Number,
    "y-min": Number,
    "x-max": Number,
    "y-max": Number,
  },
};
</script>

<style lang="scss" scoped>
.box {
  position: absolute;
  border: 2px #f30b0b solid;
}
</style>
