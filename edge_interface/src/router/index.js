import Vue from 'vue';
import Router from 'vue-router';
import AllItems from '@/components/AllItems.vue';
import ItemDetail from '@/components/ItemDetail.vue';
import TriggerView from '@/components/TriggerView.vue';
import ConfigView from '@/components/ConfigView.vue';

Vue.use(Router);

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'AllItems',
      component: AllItems
    },
    {
      path: '/item/:id',
      name: 'ItemDetail',
      component: ItemDetail
    },
    {
      path: '/trigger',
      name: 'TriggerView',
      component: TriggerView
    },
    {
      path: '/configs',
      component: ConfigView,
    }
  ]
});