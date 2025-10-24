import { createI18n } from 'vue-i18n'
import zhCN from './locales/zh-CN.json'
import enUS from './locales/en-US.json'
import jaJP from './locales/ja-JP.json'

// 从 localStorage 获取语言设置,默认中文
const savedLocale = localStorage.getItem('locale') || 'zh-CN'

const i18n = createI18n({
  legacy: false,
  locale: savedLocale,
  fallbackLocale: 'zh-CN',
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS,
    'ja-JP': jaJP
  },
  globalInjection: true,
  silentTranslationWarn: true,
  silentFallbackWarn: true
})

export default i18n

// 切换语言的工具函数
export function setLocale(locale) {
  i18n.global.locale.value = locale
  localStorage.setItem('locale', locale)
  
  // 更新 Element Plus 的语言
  return locale
}

// 获取当前语言
export function getLocale() {
  return i18n.global.locale.value
}
