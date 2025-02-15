import Vue from 'vue';
import Router from 'vue-router';
import AllItemsView from '@/components/AllItemsView.vue';
import ItemDetailView from '@/components/ItemDetailView.vue';
import TriggerView from '@/components/TriggerView.vue';
import ConfigView from '@/components/ConfigView.vue';
import ActiveConfigView from '@/components/ActiveConfigView.vue';
import NewConfigView from '@/components/NewConfigView.vue';

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
      name: 'ConfigView',
      component: ConfigView
    },
    {
      path: '/configs/active',
      name: 'ActiveConfigView',
      component: ActiveConfigView
    },
    {
      path: '/configs/new',
      name: 'NewConfigView',
      component: NewConfigView
    }
  ]
});