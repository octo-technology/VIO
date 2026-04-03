<template>
  <v-app>
    <StatusBar />
    <v-navigation-drawer :rail="rail" permanent>
      <v-list nav>
        <v-list-item
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          :prepend-icon="item.icon"
          :title="item.title"
        />
      </v-list>
      <template #append>
        <v-list nav>
          <v-list-item
            :prepend-icon="rail ? 'mdi-chevron-right' : 'mdi-chevron-left'"
            :title="rail ? '' : 'Collapse'"
            @click="rail = !rail"
          />
        </v-list>
      </template>
    </v-navigation-drawer>
    <v-main>
      <router-view />
    </v-main>
  </v-app>
</template>

<script setup>
import { ref } from 'vue'
import StatusBar from './components/StatusBar.vue'

const rail = ref(false)

const navItems = [
  { to: '/operator', icon: 'mdi-monitor-eye', title: 'Live Inspection' },
  { to: '/technician', icon: 'mdi-wrench', title: 'Configuration' },
  { to: '/admin', icon: 'mdi-shield-account', title: 'Administration' },
]
</script>
