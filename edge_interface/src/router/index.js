import Vue from 'vue';
import Router from 'vue-router';
import AllItemsView from '@/components/AllItemsView.vue';
import AllConfigsView from '@/components/AllConfigsView.vue';
import ItemDetailView from '@/components/ItemDetailView.vue';
import TriggerView from '@/components/TriggerView.vue';
import ActiveConfigView from '@/components/ActiveConfigView.vue';

Vue.use(Router);

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'AllItemsView',
      component: AllItemsView
    },
    {
      path: '/item/:id',
      name: 'ItemDetailView',
      component: ItemDetailView
    },
    {
      path: '/trigger',
      name: 'TriggerView',
      component: TriggerView
    },
    {
      path: '/configs',
      name: 'AllConfigsView',
      component: AllConfigsView
    },
    {
      path: '/configs/active',
      name: 'ActiveConfigView',
      component: ActiveConfigView
    }
  ]
});