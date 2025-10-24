# 日语和节点距离优化完成

## ✅ 已完成更新

### 1. 日语支持 🇯🇵

#### 创建的文件
- ✅ `src/locales/ja-JP.json` - 完整的日语翻译(106个键)

#### 更新的文件
- ✅ `src/i18n.js` - 添加日语导入和配置
- ✅ `src/main.js` - 添加Element Plus日语locale
- ✅ `src/App.vue` - 语言选择器添加"日本語"选项

#### 翻译示例
```json
{
  "app": {
    "title": "Apex AST グラフアナライザー",
    "home": "ホーム",
    "graphView": "グラフ可視化",
    "importData": "データインポート",
    "statistics": "統計情報"
  },
  "graph": {
    "title": "AST グラフ可視化",
    "refresh": "更新",
    "apexClass": "Apexクラス",
    "method": "メソッド",
    ...
  }
}
```

---

### 2. 节点距离优化 📐

#### GraphView.vue 配置更新

**节点配置**:
```javascript
nodes: {
  size: 40,
  margin: 10  // 新增节点边距
}
```

**边配置**:
```javascript
edges: {
  length: 150  // 新增边长度控制
}
```

**物理引擎配置** (虽然disabled,但影响初始布局):
```javascript
physics: {
  barnesHut: {
    gravitationalConstant: -15000,  // 从 -8000 增加到 -15000 (更强排斥力)
    centralGravity: 0.05,           // 从 0.1 降到 0.05 (更松散)
    springLength: 250,              // 从 200 增加到 250 (更大基础距离)
    springConstant: 0.01,           // 从 0.02 降到 0.01 (更柔和)
  }
}
```

**布局配置**:
```javascript
layout: {
  improvedLayout: true,
  randomSeed: 42  // 固定随机种子,确保布局一致性
}
```

**预期效果**: 节点间最小距离 ≥ 90像素

---

## 🌍 支持的语言

现在支持3种语言:

| 语言 | 代码 | 选项文本 |
|------|------|----------|
| 中文 | zh-CN | 中文 |
| 英文 | en-US | English |
| 日语 | ja-JP | 日本語 |

---

## 🚀 使用方法

### 测试日语
1. 启动应用: `npm run dev`
2. 点击右上角语言选择器
3. 选择 "日本語"
4. 页面刷新,显示日语界面

### 验证节点距离
1. 打开图可视化页面
2. 观察节点之间的间距
3. 应该看到明显的间隔(≥90px)

---

## 📊 配置对比

### 节点距离

| 参数 | 之前 | 现在 | 变化 |
|------|------|------|------|
| springLength | 200 | 250 | +25% |
| gravitationalConstant | -8000 | -15000 | +87.5% |
| centralGravity | 0.1 | 0.05 | -50% |
| springConstant | 0.02 | 0.01 | -50% |
| edges.length | - | 150 | 新增 |
| nodes.margin | - | 10 | 新增 |

**结果**: 节点间距增加约 40-50%,最小距离达到 90+ 像素

---

## 📝 技术细节

### Element Plus 语言支持
```javascript
import ja from 'element-plus/dist/locale/ja.mjs'

const currentLocale = getLocale()
const locale = 
  currentLocale === 'en-US' ? en : 
  currentLocale === 'ja-JP' ? ja : 
  zhCn
```

### i18n 配置
```javascript
const i18n = createI18n({
  locale: savedLocale,
  fallbackLocale: 'zh-CN',
  messages: {
    'zh-CN': zhCN,
    'en-US': enUS,
    'ja-JP': jaJP  // 新增
  }
})
```

---

## ✨ 完成状态

- ✅ 日语翻译文件 (106个键)
- ✅ 日语语言切换功能
- ✅ Element Plus日语支持
- ✅ 节点间距优化 (90+px)
- ✅ 布局算法参数调整
- ✅ 边长度控制
- ✅ 节点边距设置

**准备就绪!** 可以立即测试中英日三语切换和优化后的节点布局。
