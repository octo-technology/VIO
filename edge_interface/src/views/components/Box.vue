<template>
  <a class="block-link" @click="onClick()">
    <div class="box box-defect" :style="{
        top: yMin + 'px',
        left: xMin + 'px',
        width: xMax - xMin + 'px',
        height: yMax - yMin + 'px'
      }">
      <div v-if="dialog" class="dialog">
        <v-btn small>Wrinkle</v-btn>
        <v-btn small>Acceptable</v-btn>
        <v-btn small>Not wrinkle</v-btn>
      </div>
    </div>


  </a>
</template>

<script>
export default {
  name: "box",
  props: ["identity", "x-min", "y-min", "x-max", "y-max"],
  data: () => ({
    dialog: false
  }),
  methods: {
    onClick() {
      // this.dialog = !this.dialog;
      // alert(JSON.stringify(this.identity, null, 2))
    }
  }
};
</script>

<style lang="scss" scoped>
.box {
  position: absolute;
  user-select: none;
}

.box-defect {
  border: 2px #f30b0b solid;

}

.block-link {
  display: block;
}

.dialog {
  text-align: center;
  margin-top: -30px;
}
.dialog .v-btn {
  margin: 2px;
}
</style>
