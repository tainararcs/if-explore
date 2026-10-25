import { createApp } from 'vue'
import './index.css'
import App from './App.vue'
import { i18n } from './lib/i18n'
import { router } from './router'

createApp(App).use(i18n).use(router).mount('#app')
