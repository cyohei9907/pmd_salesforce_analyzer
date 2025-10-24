# 国际化迁移指南

## 已完成的工作

### 1. 安装依赖 ✅
- vue-i18n@^9.8.0
- @intlify/unplugin-vue-i18n@^2.0.0

### 2. 配置文件 ✅
- `vite.config.js` - 添加 VueI18nPlugin
- `src/i18n.js` - i18n 实例配置
- `src/main.js` - 集成 i18n 到 Vue 应用
- `src/App.vue` - 添加语言切换功能

### 3. 语言文件 ✅
- `src/locales/zh-CN.json` - 中文翻译
- `src/locales/en-US.json` - 英文翻译

### 4. 性能优化 ✅
- 禁用物理引擎动画 (`physics.enabled: false`)
- 禁用稳定化动画 (`stabilization.enabled: false`)
- 禁用悬停效果 (`interaction.hover: false`)
- 启用拖拽时隐藏边 (`hideEdgesOnDrag: true`)
- 启用缩放时隐藏边 (`hideEdgesOnZoom: true`)

## 使用方法

### 在组件中使用 i18n

```vue
<template>
  <div>
    <!-- 使用 $t() 函数 -->
    <h1>{{ $t('graph.title') }}</h1>
    <el-button>{{ $t('common.refresh') }}</el-button>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// 在 JS 中使用
const message = t('common.success')
</script>
```

### 翻译键命名规范

所有翻译键已按模块组织:
- `app.*` - 应用级别(标题、导航)
- `home.*` - 首页
- `graph.*` - 图可视化
- `import.*` - 导入数据
- `stats.*` - 统计信息
- `common.*` - 通用文本

### 待更新的组件

需要将硬编码的中文文本替换为 `$t()` 调用:

#### 1. GraphView.vue
查找并替换:
- "AST 图可视化" → `{{ $t('graph.title') }}`
- "刷新" → `{{ $t('common.refresh') }}`
- "适应窗口" → `{{ $t('graph.fitView') }}`
- "图例(点击过滤)" → `{{ $t('graph.legend') }}`
- "Apex类" → `{{ $t('graph.apexClass') }}`
- "方法" → `{{ $t('graph.method') }}`
- "SOQL查询" → `{{ $t('graph.soqlQuery') }}`
- "DML操作" → `{{ $t('graph.dmlOperation') }}`
- "清除过滤" → `{{ $t('graph.clearFilter') }}`
- "节点详情" → `{{ $t('graph.nodeDetails') }}`
- 等等...

#### 2. ImportData.vue
查找并替换:
- "导入 AST 数据" → `{{ $t('import.title') }}`
- "导入单个文件" → `{{ $t('import.importFile') }}`
- "导入目录" → `{{ $t('import.importDirectory') }}`
- 等等...

#### 3. Statistics.vue
查找并替换:
- "统计信息" → `{{ $t('stats.title') }}`
- "概览" → `{{ $t('stats.overview') }}`
- 等等...

#### 4. Home.vue
查找并替换:
- "欢迎使用 Apex AST 图分析器" → `{{ $t('home.welcome') }}`
- 等等...

### 快速替换示例 (GraphView.vue)

**模板部分:**
```vue
<!-- 原来 -->
<span>AST 图可视化</span>

<!-- 替换为 -->
<span>{{ $t('graph.title') }}</span>

<!-- 原来 -->
<el-button @click="loadGraph">刷新</el-button>

<!-- 替换为 -->
<el-button @click="loadGraph">{{ $t('common.refresh') }}</el-button>
```

**脚本部分:**
```vue
<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()

// 原来
ElMessage.success('图数据加载成功')

// 替换为
ElMessage.success(t('graph.loadSuccess'))
</script>
```

### 语言切换

语言切换器已添加到 App.vue 的顶部栏右侧。用户可以在中文和英文之间切换。

### 添加新翻译

1. 编辑 `src/locales/zh-CN.json` 添加中文
2. 编辑 `src/locales/en-US.json` 添加对应的英文
3. 在组件中使用 `$t('your.key')`

## 性能优化说明

### 禁用的动画效果

为了解决卡顿问题,已做以下优化:

1. **禁用物理引擎** - 节点不再自动移动和碰撞检测
2. **禁用稳定化** - 加载后立即显示,无动画过渡
3. **禁用悬停** - 减少鼠标移动时的重绘
4. **优化边的显示** - 拖拽和缩放时隐藏边以提升性能

### 如果需要重新启用动画

编辑 `GraphView.vue` 中的 options:
```javascript
physics: {
  enabled: true,  // 改为 true
  // ...
},
stabilization: {
  enabled: true,  // 改为 true
  iterations: 100
}
```

## 测试

1. 启动应用: `npm run dev`
2. 点击右上角语言选择器,切换到 English
3. 检查所有页面的文本是否正确翻译
4. 测试图可视化的性能是否改善

## 下一步

建议按以下顺序更新组件:
1. ✅ App.vue (已完成)
2. ⏳ GraphView.vue (需要更新)
3. ⏳ ImportData.vue (需要更新)
4. ⏳ Statistics.vue (需要更新)
5. ⏳ Home.vue (需要更新)
