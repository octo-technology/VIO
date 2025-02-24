<template>
  <v-container>
    <v-row>
      <v-col cols="12">
        <v-card>
          <v-card-title class="centered">
            <v-select
              v-model="selectedItemId"
              :items="itemIds"
              label="Select Item ID"
              @change="fetchItem"
              class="max-width-500"
            ></v-select>
          </v-card-title>
          <v-card-subtitle v-if="item.id">
            <item-details :item="item"></item-details>
          </v-card-subtitle>
        </v-card>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import ApiService from '@/services/ApiService.js';
import ItemDetails from './ItemDetails.vue';

export default {
  name: 'ItemDetailView',
  components: {
    ItemDetails
  },
  data() {
    return {
      item: {},
      itemIds: [],
      selectedItemId: null,
      showPredictions: {}
    };
  },
  created() {
    this.fetchItemIds();
    const itemId = this.$route.params.id;
    if (itemId) {
      this.selectedItemId = itemId;
      this.fetchItem();
    }
  },
  watch: {
    '$route.params.id': function(newId) {
      if (newId) {
        this.selectedItemId = newId;
        this.fetchItem();
      } else {
        this.item = {};
        this.selectedItemId = null;
      }
    }
  },
  methods: {
    fetchItemIds() {
      ApiService.getItems()
        .then(response => {
          // Sort items by creation date
          const sortedItems = response.data.sort((a, b) => new Date(a.creation_date) - new Date(b.creation_date));
          this.itemIds = sortedItems.map(item => item.id);
        })
        .catch(error => {
          console.error('Error fetching item IDs:', error);
        });
    },
    fetchItem() {
      if (!this.selectedItemId) return;
      ApiService.getItem(this.selectedItemId)
        .then(response => {
          this.item = response.data;
          this.$set(this.showPredictions, this.item.id, false);
        })
        .catch(error => {
          console.error('Error fetching item:', error);
        });
    }
  }
};
</script>

<style scoped>
.centered {
  display: flex;
  justify-content: center;
}

.max-width-500 {
  max-width: 500px;
}
</style>