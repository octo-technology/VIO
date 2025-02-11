<template>
  <v-app>
    <v-app-bar app>
      <v-toolbar-title>Visual Inspection Orchestrator</v-toolbar-title>
      <v-spacer></v-spacer>
      <router-link to="/" exact>
        <v-btn text :class="{ active: $route.path === '/' }">All Items</v-btn>
      </router-link>
      <router-link to="/item/1">
        <v-btn text :class="{ active: $route.path.startsWith('/item') }">Item Detail</v-btn>
      </router-link>
      <router-link to="/trigger">
        <v-btn text :class="{ active: $route.path === '/trigger' }">Trigger</v-btn>
      </router-link>
      <router-link to="/configs">
        <v-btn text :class="{ active: $route.path === '/configs' }">Configs</v-btn>
      </router-link>
    </v-app-bar>
    <v-main>
      <router-view></router-view>
    </v-main>
  </v-app>
</template>

<script>
export default {
  name: 'App'
};
</script>

<style scoped>
.active {
  background-color: rgba(0, 0, 0, 0.1); /* Highlight color for active link */
}
</style>
