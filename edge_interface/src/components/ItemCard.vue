<template>
  <v-card tile>
    <v-list-item>
      <v-list-item-content>
        <v-list-item-title class="headline mb-1">{{
          serial_number
        }}</v-list-item-title>
      </v-list-item-content>

      <div v-show="has_decision">
        <v-list-item-avatar
          tile
          size="40"
          :color="getDecisionState === 'OK' ? 'green' : 'red'"
          class="mr-0"
          >{{ getDecisionState }}
        </v-list-item-avatar>
      </div>
    </v-list-item>

    <v-card-text class="text--primary">
      <div v-show="has_category">
        <h3>Category:</h3>
        {{ get_category }}
        <h3>Received time:</h3>
        {{ get_received_time }}
      </div>
      <div v-show="has_decision">
        <h3>Internals:</h3>
        <ul>
          <li v-for="(element, key) in get_decision" :key="key">
            {{ key }}: {{ element }}
          </li>
        </ul>
      </div>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: "itemcard",
  props: ["item"],
  computed: {
    has_category() {
      return (
        this.item != null &&
        this.item != undefined &&
        this.item.category != undefined &&
        this.item.category != null
      );
    },
    has_received_time() {
      return (
        this.item != null &&
        this.item != undefined &&
        this.item.received_time != undefined &&
        this.item.received_time != null
      );
    },
    has_decision() {
      return (
        this.item != null &&
        this.item != undefined &&
        this.item.decision != undefined &&
        this.item.decision != null
      );
    },
    has_serial_number() {
      return (
        this.item != null &&
        this.item != undefined &&
        this.item.serial_number != undefined &&
        this.item.serial_number != null
      );
    },
    serial_number() {
      if (this.has_serial_number) return this.item.serial_number;
      else return "UNKNOW_SERIAL";
    },
    get_category() {
      if (this.has_category) return this.item.category;
      else return {};
    },
    get_received_time() {
      if (this.has_received_time) return this.item.received_time;
      else return {};
    },
    getDecisionState() {
      if (this.has_decision) return this.item.decision;
      else return null;
    }
  }
};
</script>
<style lang="scss" scoped></style>
