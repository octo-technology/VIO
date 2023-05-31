<template>
  <v-app id="inspire">
    <v-navigation-drawer v-model="drawer" app clipped>
      <v-list dense>
        <v-list-item link to="/">
          <v-list-item-action>
            <v-icon>mdi-cog</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>
              List
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item link to="/upload-files">
          <v-list-item-action>
            <v-icon>mdi-cloud-upload</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>
              Upload
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item link to="/upload-camera">
          <v-list-item-action>
            <v-icon>mdi-camera</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>
              Camera
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item link to="/trigger">
          <v-list-item-action>
            <v-icon>mdi-cloud-upload</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>
              Trigger
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item link to="/config">
          <v-list-item-action>
            <v-icon>mdi-cog</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>
              Config
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
        <v-list-item link to="/about">
          <v-list-item-action>
            <v-icon>mdi-view-dashboard</v-icon>
          </v-list-item-action>
          <v-list-item-content>
            <v-list-item-title>
              About
            </v-list-item-title>
          </v-list-item-content>
        </v-list-item>
      </v-list>
    </v-navigation-drawer>

    <v-app-bar app clipped-left>
      <v-app-bar-nav-icon @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
      <v-toolbar-title>VIO UI</v-toolbar-title>
    </v-app-bar>

    <v-main>
      <v-container fluid>
        <v-row align="start">
          <router-view></router-view>
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
  name: "App",
  props: {
    source: String
  },

  data: () => ({
    drawer: false
  }),

  created() {
    this.$vuetify.theme.dark = false;
  }
};
</script>
