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
        <!-- <v-btn fab absolute top left tile @click.stop="drawer = !drawer"
          class="btn-invisible"><v-icon>mdi-menu</v-icon></v-btn> -->
      </v-container>

    </v-main>

    <v-dialog v-model="dialog" fullscreen hide-overlay>
      <modal-profile @close="onClose($event)"></modal-profile>
    </v-dialog>
    <!--    <v-footer app>-->
    <!--      <span>&copy; 2023</span>-->
    <!--    </v-footer>-->
  </v-app>
</template>

<script>
import ModalProfile from './views/components/ModalProfile.vue';
import SidePanel from "./views/navigation/SidePanel.vue"

export default {
  name: 'App',
  props: {
    source: String
  },
  components: { SidePanel, ModalProfile },
  data: () => ({
    drawer: false
  })
}
</script>

<style scoped>
.btn-invisible {
  margin-top: 30px;
  background-color: transparent !important;
}
</style>