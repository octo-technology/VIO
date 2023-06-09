<template>
  <v-app id="main">
    <v-app-bar app clipped-left color="#01579B">
      <v-btn icon to="/">
        <v-icon>mdi-home</v-icon>
      </v-btn>
      <v-toolbar-title>VIO UI</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-tooltip bottom>
        <template v-slot:activator="{ on, attrs }">
          <v-btn icon to="/config" v-bind="attrs" v-on="on">
            <v-icon>mdi-cog</v-icon>
          </v-btn>
        </template>
        <span>Settings</span>
      </v-tooltip>
    </v-app-bar>
    <v-main>
      <v-container fluid>
        <v-row align="start">
          <router-view />
        </v-row>
      </v-container>
    </v-main>

    <v-footer app>
      <span>&copy; 2023</span>
    </v-footer>
  </v-app>
</template>

<script>
export default {
  name: 'App',
  props: {
    source: String
  },

  data: () => ({
    drawer: false
  })
}
</script>
