<template>
  <v-app id="inspire">

    <v-app-bar app dense>
      <v-app-bar-nav-icon @click.stop="drawer = !drawer"></v-app-bar-nav-icon>
      <v-toolbar-title>V.IO</v-toolbar-title>
      <!-- <v-spacer></v-spacer> -->
      <!-- <v-btn icon>
        <v-icon @click.stop="dialog = !dialog">mdi-account</v-icon>
      </v-btn> -->
    </v-app-bar>
    <side-panel v-if="drawer"></side-panel>

    <v-main>
      <v-container fluid>
        <v-row align="start">
          <router-view></router-view>
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
  name: "App",
  props: {
    source: String
  },
  components: { SidePanel, ModalProfile },
  data: () => ({
    drawer: false,
    dialog: false
  }),

  created() {
    this.$vuetify.theme.dark = true;
  },
  methods: {
    onClose(value) {
      this.dialog = value;
    }
  }
};
</script>

<style scoped>
.btn-invisible {
  margin-top: 30px;
  background-color: transparent !important;
}
</style>