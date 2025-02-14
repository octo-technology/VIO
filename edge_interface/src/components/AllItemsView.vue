<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-alert v-if="error" type="error" dismissible @input="error = false">
          {{ errorMessage }}
        </v-alert>
      </v-col>
    </v-row>
    <v-row v-if="items.length === 0">
      <v-col cols="12">
        <v-alert type="info">
          No data available
        </v-alert>
      </v-col>
    </v-row>
    <v-row v-else>
      <v-col v-for="item in items" :key="item.id" cols="12" md="8">
        <item-details :item="item"></item-details>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import ApiService from '@/services/ApiService.js';
import ItemDetails from './ItemDetails.vue';

export default {
  name: 'AllItemsView',
  components: {
    ItemDetails
  },
  data() {
    return {
      items: [],
      error: false,
      errorMessage: ''
    };
  },
  created() {
    this.fetchItems();
  },
  methods: {
    fetchItems() {
      ApiService.getItems()
        .then(response => {
          this.items = response.data;
          this.sortItemsByCreationDate();
        })
        .catch(error => {
          console.error('Error fetching items:', error);
          const detail = error.response && error.response.data && error.response.data.detail;
          this.errorMessage = 'Error fetching items: ' + (detail || error.message || 'Unknown error');
          this.error = true;
        });
    },
    sortItemsByCreationDate() {
      this.items.sort((a, b) => new Date(b.creation_date) - new Date(a.creation_date));
    }
  }
};
</script>

<style scoped>
.cursor-pointer {
  cursor: pointer;
}
.decision-ok {
  color: green;
}
.decision-ko {
  color: red;
}
.decision-no-decision {
  color: lightgray;
}
</style>