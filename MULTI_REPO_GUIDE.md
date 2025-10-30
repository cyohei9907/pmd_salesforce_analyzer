# 多仓库功能实现指南

## 概述
本系统现已支持管理多个Git仓库,每个仓库的代码分析和图数据独立存储和展示。

## 后端实现 ✅ (已完成)

### 1. 数据模型
- **Repository模型**: 存储仓库信息(名称、URL、分支、本地路径等)
- **ASTFile模型**: 与Repository关联,支持多仓库的AST文件管理

### 2. 目录结构
```
project/
  ├── dreamhouse-lwc/      # Git仓库1
  ├── lwc-recipes/         # Git仓库2
  └── ...                  # 更多仓库

output/ast/
  ├── dreamhouse-lwc/      # 仓库1的AST文件
  ├── lwc-recipes/         # 仓库2的AST文件
  └── ...

graphdata/
  ├── entities.json        # 所有实体(包含repository属性)
  └── relations.json       # 所有关系
```

### 3. API端点

#### 仓库管理
- `GET /api/repositories/` - 获取所有仓库列表
- `POST /api/repositories/` - 添加新仓库
- `GET /api/repositories/<id>/` - 获取仓库详情
- `PUT /api/repositories/<id>/` - 更新仓库信息
- `DELETE /api/repositories/<id>/` - 删除仓库

#### 仓库操作
- `POST /api/repositories/switch/` - 切换活动仓库
- `POST /api/repositories/clone/` - 克隆并注册仓库
- `GET /api/repositories/<id>/graph/` - 获取指定仓库的图数据

#### 示例请求

**克隆并注册仓库:**
```json
POST /api/repositories/clone/
{
  "repo_url": "https://github.com/trailheadapps/dreamhouse-lwc.git",
  "branch": "main",
  "apex_dir": "force-app/main/default/classes",
  "force": false,
  "auto_import": true,
  "set_active": true
}
```

**切换活动仓库:**
```json
POST /api/repositories/switch/
{
  "repo_id": 1
}
```

**获取仓库图数据:**
```
GET /api/repositories/1/graph/
```

## 前端实现 📝 (待实现)

### 1. 仓库选择器组件

创建 `frontend/src/components/RepositorySelector.vue`:

```vue
<template>
  <div class="repository-selector">
    <el-select 
      v-model="selectedRepoId" 
      @change="handleRepoChange"
      placeholder="选择仓库"
      class="repo-select"
    >
      <el-option
        v-for="repo in repositories"
        :key="repo.id"
        :label="repo.name"
        :value="repo.id"
      >
        <span class="repo-option">
          <el-icon v-if="repo.is_active" class="active-icon">
            <Check />
          </el-icon>
          {{ repo.name }}
          <el-tag size="small" class="file-count">
            {{ repo.ast_files_count }} files
          </el-tag>
        </span>
      </el-option>
    </el-select>
    
    <el-button 
      type="primary" 
      :icon="Plus" 
      @click="showAddDialog = true"
      class="add-repo-btn"
    >
      添加仓库
    </el-button>
    
    <!-- 添加仓库对话框 -->
    <el-dialog v-model="showAddDialog" title="添加Git仓库" width="600px">
      <el-form :model="newRepo" label-width="120px">
        <el-form-item label="仓库URL">
          <el-input v-model="newRepo.repo_url" placeholder="https://github.com/..."/>
        </el-form-item>
        <el-form-item label="分支">
          <el-input v-model="newRepo.branch" placeholder="main"/>
        </el-form-item>
        <el-form-item label="Apex目录">
          <el-input v-model="newRepo.apex_dir" placeholder="force-app/main/default/classes"/>
        </el-form-item>
        <el-form-item label="设为活动仓库">
          <el-switch v-model="newRepo.set_active"/>
        </el-form-item>
        <el-form-item label="自动导入">
          <el-switch v-model="newRepo.auto_import"/>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showAddDialog = false">取消</el-button>
        <el-button type="primary" @click="handleAddRepository" :loading="adding">
          添加并克隆
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Plus, Check } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const repositories = ref([])
const selectedRepoId = ref(null)
const showAddDialog = ref(false)
const adding = ref(false)

const newRepo = ref({
  repo_url: '',
  branch: 'main',
  apex_dir: 'force-app/main/default/classes',
  set_active: true,
  auto_import: true,
  force: false
})

const emit = defineEmits(['repo-changed'])

// 加载仓库列表
const loadRepositories = async () => {
  try {
    const response = await api.get('/repositories/')
    repositories.value = response.data.repositories
    
    // 设置当前活动仓库
    const activeRepo = repositories.value.find(r => r.is_active)
    if (activeRepo) {
      selectedRepoId.value = activeRepo.id
    }
  } catch (error) {
    ElMessage.error('加载仓库列表失败')
    console.error(error)
  }
}

// 切换仓库
const handleRepoChange = async (repoId) => {
  try {
    await api.post('/repositories/switch/', { repo_id: repoId })
    await loadRepositories()
    emit('repo-changed', repoId)
    ElMessage.success('已切换仓库')
  } catch (error) {
    ElMessage.error('切换仓库失败')
    console.error(error)
  }
}

// 添加仓库
const handleAddRepository = async () => {
  adding.value = true
  try {
    const response = await api.post('/repositories/clone/', newRepo.value)
    ElMessage.success(response.data.message)
    showAddDialog.value = false
    await loadRepositories()
    
    // 重置表单
    newRepo.value = {
      repo_url: '',
      branch: 'main',
      apex_dir: 'force-app/main/default/classes',
      set_active: true,
      auto_import: true,
      force: false
    }
  } catch (error) {
    ElMessage.error(error.response?.data?.error || '添加仓库失败')
    console.error(error)
  } finally {
    adding.value = false
  }
}

onMounted(() => {
  loadRepositories()
})
</script>

<style scoped>
.repository-selector {
  display: flex;
  gap: 10px;
  align-items: center;
  margin-bottom: 20px;
}

.repo-select {
  min-width: 300px;
}

.repo-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.active-icon {
  color: #67c23a;
}

.file-count {
  margin-left: auto;
}
</style>
```

### 2. 更新主视图

在 `frontend/src/views/GraphView.vue` 或主页面中集成:

```vue
<template>
  <div class="graph-view">
    <!-- 添加仓库选择器 -->
    <RepositorySelector @repo-changed="handleRepoChange" />
    
    <!-- 原有的图形展示组件 -->
    <GraphDisplay :repository-id="currentRepoId" />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import RepositorySelector from '@/components/RepositorySelector.vue'
import GraphDisplay from '@/components/GraphDisplay.vue'

const currentRepoId = ref(null)

const handleRepoChange = async (repoId) => {
  currentRepoId.value = repoId
  // 重新加载图数据
  await loadGraphData(repoId)
}

const loadGraphData = async (repoId) => {
  // 调用API获取该仓库的图数据
  const response = await api.get(`/repositories/${repoId}/graph/`)
  // 更新图形展示
  // ...
}
</script>
```

### 3. 更新API调用

在 `frontend/src/api/index.js` 中确保正确配置:

```javascript
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000/api',
  timeout: 30000
})

export default api
```

## 使用流程

### 1. 添加仓库
1. 点击"添加仓库"按钮
2. 输入Git仓库URL(如: https://github.com/trailheadapps/dreamhouse-lwc.git)
3. 配置分支和Apex目录
4. 点击"添加并克隆"
5. 系统自动克隆、分析并导入代码

### 2. 切换仓库查看
1. 使用下拉菜单选择不同的仓库
2. 图形界面自动更新显示该仓库的代码结构

### 3. 管理仓库
- 在仓库列表中可以查看每个仓库的文件数量
- 可以删除不需要的仓库
- 当前活动仓库会有特殊标记

## 测试步骤

1. **测试仓库克隆:**
```bash
# 使用API测试
curl -X POST http://localhost:8000/api/repositories/clone/ \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/trailheadapps/dreamhouse-lwc.git",
    "branch": "main",
    "auto_import": true,
    "set_active": true
  }'
```

2. **查看仓库列表:**
```bash
curl http://localhost:8000/api/repositories/
```

3. **获取仓库图数据:**
```bash
curl http://localhost:8000/api/repositories/1/graph/
```

## 注意事项

1. **性能考虑**: 大型仓库可能需要较长时间进行分析
2. **存储空间**: 每个仓库都会占用本地存储空间
3. **数据隔离**: 不同仓库的数据完全隔离,互不影响
4. **并发克隆**: 建议一次只克隆一个仓库,避免资源竞争

## 下一步优化

- [ ] 添加仓库分析进度显示
- [ ] 支持仓库更新(git pull)
- [ ] 添加仓库标签和分类
- [ ] 支持私有仓库(需要认证)
- [ ] 批量导入多个仓库
- [ ] 仓库对比功能

