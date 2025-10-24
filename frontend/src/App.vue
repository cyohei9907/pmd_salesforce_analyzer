<template>
  <div id="app">
    <el-container style="height: 100vh">
      <!-- 侧边栏 -->
      <el-aside :width="isCollapse ? '64px' : '250px'" class="sidebar-transition">
        <div class="logo" style="color: #333; height: 60px; display: flex; align-items: center; justify-content: center; font-size: 18px; font-weight: bold; overflow: hidden; white-space: nowrap; border-bottom: 2px solid #333">
          <el-icon style="font-size: 24px; vertical-align: middle"><Platform /></el-icon>
          <transition name="logo-fade">
            <span v-if="!isCollapse" style="margin-left: 8px">Apex AST Analyzer</span>
          </transition>
        </div>
        <el-menu
          :default-active="$route.path"
          router
          :collapse="isCollapse"
          background-color="#fff"
          text-color="#333"
          active-text-color="#000"
        >
          <el-menu-item index="/">
            <el-icon><HomeFilled /></el-icon>
            <template #title>{{ $t('app.home') }}</template>
          </el-menu-item>
          <el-menu-item index="/graph">
            <el-icon><Share /></el-icon>
            <template #title>{{ $t('app.graphView') }}</template>
          </el-menu-item>
          <el-menu-item index="/import">
            <el-icon><Upload /></el-icon>
            <template #title>{{ $t('app.importData') }}</template>
          </el-menu-item>
          <el-menu-item index="/statistics">
            <el-icon><DataAnalysis /></el-icon>
            <template #title>{{ $t('app.statistics') }}</template>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区域 -->
      <el-container>
        <!-- 顶部栏 -->
        <el-header style="background-color: #fff; border-bottom: 2px solid #333">
          <div style="display: flex; align-items: center; height: 100%; justify-content: space-between">
            <div style="display: flex; align-items: center; gap: 15px">
              <!-- 收起/展开按钮 -->
              <el-button 
                @click="isCollapse = !isCollapse"
                :icon="isCollapse ? DArrowRight : DArrowLeft"
                circle
                size="default"
                class="toggle-sidebar-btn"
              />
              <h2 style="margin: 0">{{ pageTitle }}</h2>
            </div>
            <div style="display: flex; align-items: center; gap: 10px">
              <el-select 
                v-model="currentLocale" 
                @change="handleLocaleChange" 
                style="width: 140px"
                class="wireframe-select"
              >
                <el-option label="中文" value="zh-CN" />
                <el-option label="English" value="en-US" />
                <el-option label="日本語" value="ja-JP" />
              </el-select>
              <el-button @click="refreshData" :icon="Refresh" circle />
            </div>
          </div>
        </el-header>

        <!-- 内容区域 -->
        <el-main style="background-color: #fafafa">
          <router-view v-slot="{ Component }">
            <keep-alive>
              <component :is="Component" :key="$route.path" />
            </keep-alive>
          </router-view>
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup>
import { ref, computed, provide } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Refresh, DArrowRight, DArrowLeft } from '@element-plus/icons-vue'
import { setLocale, getLocale } from './i18n'

const route = useRoute()
const { t } = useI18n()

const currentLocale = ref(getLocale())
const isCollapse = ref(true) // 侧边栏收起状态 - 默认收起

// 提供sidebar状态给子组件
provide('sidebarCollapsed', isCollapse)

const pageTitles = computed(() => ({
  '/': t('app.home'),
  '/graph': t('app.graphView'),
  '/import': t('app.importData'),
  '/statistics': t('app.statistics')
}))

const pageTitle = computed(() => pageTitles.value[route.path] || t('app.title'))

const handleLocaleChange = (locale) => {
  setLocale(locale)
  window.location.reload() // 重新加载以应用新语言
}

const refreshData = () => {
  window.location.reload()
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB',
    'Microsoft YaHei', Arial, sans-serif;
}

.el-aside {
  overflow-y: auto;
  overflow-x: hidden;
}

.el-aside::-webkit-scrollbar {
  width: 6px;
}

.el-aside::-webkit-scrollbar-thumb {
  background-color: rgba(255, 255, 255, 0.2);
  border-radius: 3px;
}

/* Sidebar平滑过渡 - 使用GPU加速 */
.sidebar-transition {
  background-color: #fff;
  border-right: 2px solid #333;
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
  will-change: width;
  transform: translateZ(0);
  backface-visibility: hidden;
}

/* 优化菜单过渡效果 */
.el-menu {
  transition: width 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
  border-right: none !important;
}

.el-menu-item {
  transition: padding 0.4s cubic-bezier(0.4, 0, 0.2, 1), 
              width 0.4s cubic-bezier(0.4, 0, 0.2, 1),
              background-color 0.2s !important;
}

.el-menu-item .el-icon {
  transition: margin 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

/* Logo文本淡入淡出动画 */
.logo-fade-enter-active {
  transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1) 0.1s;
}

.logo-fade-leave-active {
  transition: opacity 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

.logo-fade-enter-from,
.logo-fade-leave-to {
  opacity: 0;
}

.logo-fade-enter-to,
.logo-fade-leave-from {
  opacity: 1;
}
</style>
