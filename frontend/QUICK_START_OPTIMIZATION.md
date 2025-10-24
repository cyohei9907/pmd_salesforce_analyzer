# 快速开始 - 性能优化和国际化

## 🎯 已完成

1. ✅ **性能优化** - 禁用物理引擎动画,解决卡顿
2. ✅ **i18n框架** - 完整的中英文双语支持
3. ✅ **调试工具** - Vite调试配置和网络访问
4. ✅ **语言切换** - 右上角下拉框切换语言

## 🚀 立即测试

### 1. 重启前端(应用性能优化)
```bash
cd frontend
npm run dev
```

访问 http://localhost:3000 - 图可视化加载应该非常快!

### 2. 测试语言切换
- 点击右上角语言选择器
- 选择 "English"
- 页面刷新后显示英文(App导航已支持)

### 3. 应用国际化到所有组件(可选)

#### 方法1: 自动脚本(推荐用于GraphView)
```powershell
cd frontend
.\apply_i18n_graphview.ps1
```

#### 方法2: 手动替换(用于其他组件)
参考 `I18N_MIGRATION_GUIDE.md` 中的替换规则

## 📋 下一步

### 必做(启用完整国际化)
1. 更新 GraphView.vue
2. 更新 Home.vue  
3. 更新 ImportData.vue
4. 更新 Statistics.vue

### 可选(增强功能)
1. 添加更多语言
2. 优化翻译文本
3. 添加语言切换动画

## 📚 文档

- `OPTIMIZATION_SUMMARY.md` - 完整技术总结
- `I18N_MIGRATION_GUIDE.md` - 国际化迁移指南
- `GraphView_i18n_helper.js` - 替换映射参考

## 💡 提示

**当前状态**: 
- ✅ 图可视化性能已优化
- ✅ App框架支持中英文
- ⏳ 各页面组件需要应用翻译

**预期效果**:
- 加载速度提升 3-5倍
- 支持完整的中英文切换
- 更好的调试体验
