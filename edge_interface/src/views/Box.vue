<template>
  <div
    class="box"
    :style="{
      top: yMin + 'px',
      left: xMin + 'px',
      width: xMax - xMin + 'px',
      height: yMax - yMin + 'px'
    }"
  ></div>
</template>

<script>
export default {
  name: "Box",
  props: ["x-min", "y-min", "x-max", "y-max"]
};
</script>
