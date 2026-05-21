import { createApp } from 'vue'
import { createVuetify } from 'vuetify'
import { createPinia } from 'pinia'
import { VueQueryPlugin } from '@tanstack/vue-query'
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

import App from './App.vue'
import router from './router'
import { useHealthStore } from './features/system-health/stores/healthStore'

const vuetify = createVuetify({
  theme: {
    defaultTheme: 'light',
  },
})

const pinia = createPinia()

const app = createApp(App)
  .use(pinia)
  .use(VueQueryPlugin)
  .use(router)
  .use(vuetify)

useHealthStore().startPolling()

app.mount('#app')
