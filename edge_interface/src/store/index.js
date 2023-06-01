/* eslint-disable no-shadow */
import Vue from 'vue'
import Vuex from 'vuex'
import createPersistedState from 'vuex-persistedstate'
import ItemsService from '@/services/ItemsService.js'

Vue.use(Vuex)

export const state = {
  listItems: [],
  imagePath: null
}

export const mutations = {
  SET_ITEMS(state, listItems) {
    state.listItems = listItems
  },
  SET_IMAGE_PATH(state, imagePath) {
    state.imagePath = imagePath
  }
}

export const actions = {
  async load_items({ commit }) {
    ItemsService.getItems()
      .then(r => r.data)
      .then(items => {
        commit('SET_ITEMS', items)
      })
  }
}

export const getters = {
  getItemById: state => id => {
    return state.listItems.find(item => item.id === id)
  },
  imagePath(state) {
    return state.imagePath
  }
}

export default new Vuex.Store({
  state,
  plugins: [createPersistedState({ storage: window.sessionStorage })],
  actions,
  mutations,
  getters
})
