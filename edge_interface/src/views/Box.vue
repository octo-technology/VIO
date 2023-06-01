<template>
  <div
    class="box"
    :style="{
      top: yMin + 'px',
      left: xMin + 'px',
      width: xMax - xMin + 'px',
      height: yMax - yMin + 'px'
    }"
  />
</template>

<script>
export default {
  name: 'Box',
  props: ['x-min', 'y-min', 'x-max', 'y-max']
}
</script>

<style lang="scss" scoped>
.box {
  position: absolute;
  border: 2px #f30b0b solid;
}
</style>
