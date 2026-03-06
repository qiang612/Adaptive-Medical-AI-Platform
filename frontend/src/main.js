import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import App from './App.vue'
import router from './router'
import Permission from '@/components/Permission.vue'
import StatusTag from '@/components/StatusTag.vue'
import Pagination from '@/components/Pagination.vue'
import './style/global.css'

const app = createApp(App)
const pinia = createPinia()

// 全局注册Element Plus图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 全局注册自定义组件
app.component('Permission', Permission)
app.component('StatusTag', StatusTag)
app.component('Pagination', Pagination)

app.use(pinia)
app.use(router)
app.use(ElementPlus)
app.mount('#app')