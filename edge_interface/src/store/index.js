import Vue from "vue";
import Vuex from "vuex";
import createPersistedState from "vuex-persistedstate";

Vue.use(Vuex);
import ItemsService from "@/services/ItemsService";

export const state = {
  listItems: [],
  imagePath: null
}

export const mutations = {
  SET_ITEMS(state, list_items) {
    // Sort list from more recent to oldest
    list_items.sort((recent, old) => {
      let date_recent = new Date(recent.received_time),
        date_old = new Date(old.received_time);
      return date_old - date_recent;
    });
    state.listItems = list_items;
  },
  SET_IMAGE_PATH(state, imagePath) {
    state.imagePath = imagePath
  }
};

export const actions = {
  async load_items({ commit }) {
    ItemsService.get_items()
      .then(r => r.data)
      .then(items => {
        commit("SET_ITEMS", items);
      });
  }
};

export const getters = {
  getItemById: state => id => {
    return state.listItems.find(item => item.id === id);
  },
  imagePath(state) {
    return state.imagePath
  }
};

export default new Vuex.Store({
  state,
  plugins: [createPersistedState({ storage: window.sessionStorage })],
  actions,
  mutations,
  getters
});