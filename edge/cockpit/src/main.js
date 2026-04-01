import { createApp } from 'vue'
import { createVuetify } from 'vuetify'
import '@mdi/font/css/materialdesignicons.css'
import 'vuetify/styles'

import App from './App.vue'
import router from './router'

const vuetify = createVuetify({
  theme: {
    defaultTheme: 'light',
  },
})

createApp(App).use(router).use(vuetify).mount('#app')
