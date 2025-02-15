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
      <v-menu offset-y>
        <template v-slot:activator="{ on, attrs }">
          <v-btn icon v-bind="attrs" v-on="on" :class="{ active: $route.path.startsWith('/configs') }">
            <v-icon>mdi-cog</v-icon>
          </v-btn>
        </template>
        <v-list>
          <v-list-item @click="$router.push('/configs')">
            <v-list-item-title>View all configs</v-list-item-title>
          </v-list-item>
          <v-list-item @click="$router.push('/configs/new')">
            <v-list-item-title>Create New Config</v-list-item-title>
          </v-list-item>
          <v-list-item @click="$router.push('/configs/active')">
            <v-list-item-title>See active config</v-list-item-title>
          </v-list-item>
        </v-list>
      </v-menu>
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
