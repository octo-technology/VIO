import { createRouter, createWebHistory } from 'vue-router'

declare module 'vue-router' {
  interface RouteMeta {
    role: 'operator' | 'technician' | 'admin'
    title: string
  }
}

const routes = [
  {
    path: '/',
    redirect: '/operator',
  },
  {
    path: '/operator',
    name: 'operator',
    component: () => import('../pages/OperatorPage.vue'),
    meta: { role: 'operator' as const, title: 'Live Inspection' },
  },
  {
    path: '/technician',
    name: 'technician',
    component: () => import('../pages/TechnicianPage.vue'),
    meta: { role: 'technician' as const, title: 'Configuration' },
  },
  {
    path: '/teach',
    name: 'teach',
    component: () => import('../pages/TeachPage.vue'),
    meta: { role: 'technician' as const, title: 'Reference Bank' },
  },
  {
    path: '/admin',
    name: 'admin',
    component: () => import('../pages/AdminPage.vue'),
    meta: { role: 'admin' as const, title: 'Administration' },
  },
]

export default createRouter({
  history: createWebHistory(),
  routes,
})
