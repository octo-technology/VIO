import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/operator',
  },
  {
    path: '/operator',
    name: 'operator',
    component: () => import('../views/OperatorView.vue'),
    meta: { role: 'operator', title: 'Live Inspection' },
  },
  {
    path: '/technician',
    name: 'technician',
    component: () => import('../views/TechnicianView.vue'),
    meta: { role: 'technician', title: 'Configuration' },
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('../views/AdminView.vue'),
    meta: { role: 'admin', title: 'Administration' },
  },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
