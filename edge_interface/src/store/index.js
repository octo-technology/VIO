import Vue from "vue";
import Vuex from "vuex";
import createPersistedState from "vuex-persistedstate";
import { baseURL } from "@/services/api";

Vue.use(Vuex);
import ItemsService from "@/services/ItemsService";

const mutations = {
  SET_ITEMS(state, list_items) {
    // Sort list from more recent to oldest
    list_items.sort((recent, old) => {
      let date_recent = new Date(recent.received_time),
        date_old = new Date(old.received_time);
      return date_old - date_recent;
    });
    state.listItems = list_items;
  },
  ENRICH_ITEMS(state, list_items) {
    // Sort list from more recent to oldest

    list_items.forEach(item => {
      item.predictedItems = []

      if ('inferences' in item) {
        Object.keys(item.inferences).forEach((camera_id) => {

          item.predictedItems.push({
            camera_id: camera_id,
            inferences: item.inferences[camera_id],
            image_url: `${baseURL}/items/${item.id}/binaries/${camera_id}`,
            count_boxes: (Object.values(item.inferences[camera_id])[0] == 'NO_DECISION') ? 0 : Object.values((Object.values(item.inferences[camera_id])[0])).length
          });
        });
      }
    });
    // console.log("updated", list_items);
    state.listItems = list_items;
  }
};

const actions = {
  async load_items({ commit }) {
    ItemsService.get_items()
      .then(r => r.data)
      .then(items => {
        commit("SET_ITEMS", items);
        commit("ENRICH_ITEMS", items);
      });
  }
};

const getters = {
  getItemById: state => id => {
    // console.log(id);
    // console.log(state.listItems);
    return state.listItems.find(item => item.id === id);
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
