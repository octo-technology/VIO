import Vue from "vue";
import Vuex from "vuex";
import createPersistedState from "vuex-persistedstate";

Vue.use(Vuex);
import ItemsService from "@/services/ItemsService";

const mutations = {
  SET_ITEMS(state, list_items) {
    state.listItems = list_items;
  }
};

const actions = {
  async load_items({ commit }) {
    ItemsService.get_items()
      .then(r => r.data)
      .then(items => {
        commit("SET_ITEMS", items);
      });
  }
};

const getters = {
  getItemById: state => id => {
    console.log(id);
    console.log(state.listItems);
    return state.listItems.find(item => item._id === id);
  }
};

export default new Vuex.Store({
  state: {
    listItems: []
  },
  plugins: [createPersistedState({ storage: window.sessionStorage })],
  actions,
  mutations,
  getters
});

// https://www.npmjs.com/package/vuex-persistedstate
