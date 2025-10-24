import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './styles/wireframe.css'  // 导入线框风格主题
import * as ElementPlusIconsVue from '@element-plus/icons-vue'
import zhCn from 'element-plus/dist/locale/zh-cn.mjs'
import en from 'element-plus/dist/locale/en.mjs'
import ja from 'element-plus/dist/locale/ja.mjs'
import App from './App.vue'
import router from './router'
import i18n, { getLocale } from './i18n'

const app = createApp(App)
const pinia = createPinia()

// 注册所有图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 根据当前语言设置 Element Plus 的语言
const currentLocale = getLocale()
const locale = currentLocale === 'en-US' ? en : currentLocale === 'ja-JP' ? ja : zhCn

app.use(pinia)
app.use(router)
app.use(i18n)
app.use(ElementPlus, { locale })

app.mount('#app')
