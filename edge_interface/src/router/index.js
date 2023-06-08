import Vue from 'vue'
import VueRouter from 'vue-router'
import VUploadView from '../views/VUploadView/VUploadView.vue'
import VConfig from '../views/VConfig/VConfig.vue'

Vue.use(VueRouter)

const routes = [
  {
    path: '/',
    redirect: '/item-list'
  },
  {
    path: '/item-show/:id',
    props: true,
    name: 'item-show',
    component: () => import(/* webpackChunkName: "about" */ '../views/ItemShow.vue')
  },
  {
    path: '/test',
    props: true,
    name: 'VUploadView',
    component: VUploadView
  },
  {
    path: '/item-list',
    name: 'Item-list',
    component: () => import(/* webpackChunkName: "about" */ '../views/ItemList.vue')
  },
  {
    path: '/upload-camera',
    name: 'Upload Camera',
    component: () => import('../views/UploadView.vue')
  },
  {
    path: '/trigger',
    name: 'Trigger Capture',
    component: () => import('../views/TriggerView.vue')
  },
  {
    path: '/config',
    name: 'Config',
    component: () => import('../views/Config.vue')
  },
  {
    path: '/test_config',
    name: 'VConfig',
    component: VConfig
  }
]

const router = new VueRouter({
  routes
})

export default router
