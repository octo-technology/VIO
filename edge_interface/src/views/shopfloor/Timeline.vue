<template>
  <div v-if="state" class="timeline">
    <ol v-for="status in Object.keys(statusList)" :key="status">
      <li>
        <span class="line" v-bind:class="getColor(status)"></span>
        <span>{{ status }}</span>
      </li>
    </ol>
  </div>
</template>

<script>
export default {
  name: "component-tag",
  components: {},
  props: {
    state: String,
  },
  data: () => ({
    statusList: {
      Capture: 0,
      "Save Binaries": 1,
      Inference: 2,
      Decision: 3,
      Done: 4,
    },
  }),
  methods: {
    getColor(status) {
      if (this.statusList[status] > this.statusList[this.state]) {
        return "red";
      } else {
        return "green";
      }
    },
  },
};
</script>

<style lang="scss" scoped>
.timeline {
  padding: 2rem;
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
