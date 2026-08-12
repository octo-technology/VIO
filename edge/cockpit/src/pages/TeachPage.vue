<template>
  <v-container fluid>
    <div class="d-flex align-center mb-4">
      <span class="text-h6">Reference Bank</span>
    </div>

    <v-row v-if="isLoading">
      <v-col cols="12" md="6">
        <v-skeleton-loader type="card" />
      </v-col>
    </v-row>

    <v-row v-else-if="models.length">
      <v-col cols="12" md="6">
        <ReferenceBankCard :models="models" />
      </v-col>
    </v-row>

    <v-empty-state
      v-else
      icon="mdi-brain"
      title="No teachable models"
      subtitle="Activate a configuration whose pipeline uses an anomaly-detection model, then teach it here."
    />
  </v-container>
</template>

<script setup>
import ReferenceBankCard from '../features/anomaly-bank/components/ReferenceBankCard.vue'
import { useTeachableModels } from '../features/anomaly-bank/composables/useTeachableModels'

const { models, isLoading } = useTeachableModels()
</script>
