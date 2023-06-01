<template>
  <div class="container">
    <div>
      <h3>Trigger the capture of an item</h3>
      <h4>Just click on the button below, VIO will do the rest</h4>
    </div>

    <Inference :errorMessage="errorMessage" @update-error-message="update" />

    <div v-if="errorMessage !== null" class="no_configuration">
      <v-alert color="red" dismissible elevation="10" type="warning">{{ this.errorMessage }} </v-alert>
    </div>
  </div>
</template>

<script>
import Inference from '@/components/Inference'

export default {
  name: 'item-trigger',
  components: { Inference },
  data() {
    return {
      errorMessage: null
    }
  },
  methods: {
    update(errorMessage) {
      this.errorMessage = errorMessage
    }
  }
}
</script>

<style lang="scss" scoped>
.container {
  text-align: center;
}

.no_configuration {
  padding: 6rem 0;
}

.red {
  background: #d41928;
}

.green {
  background: #51d419;
}
</style>
