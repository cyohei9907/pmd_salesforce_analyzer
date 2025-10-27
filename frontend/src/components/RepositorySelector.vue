<template>
  <div class="repository-selector">
    <el-select 
      v-model="selectedRepoId" 
      @change="handleRepoChange"
      :placeholder="repositories.length === 0 ? '暂无仓库，请先导入' : '选择仓库'"
      class="repo-select"
      :loading="loading"
      :disabled="repositories.length === 0"
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
          <span>{{ repo.name }}</span>
          <el-tag size="small" class="file-count" type="info">
            {{ repo.ast_files_count }} files
          </el-tag>
        </span>
      </el-option>
    </el-select>
    
    <el-tag v-if="repositories.length === 0" type="warning" size="small">
      请先在"导入 AST 数据"页面克隆仓库
    </el-tag>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { Check } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import api from '@/api'

const repositories = ref([])
const selectedRepoId = ref(null)
const loading = ref(false)

const emit = defineEmits(['repo-changed'])

// 加载仓库列表
const loadRepositories = async () => {
  loading.value = true
  try {
    const data = await api.get('/repositories/')
    
    if (data.success) {
      repositories.value = data.repositories || []
      
      if (repositories.value.length === 0) {
        console.log('暂无仓库数据')
      } else {
        // 设置当前活动仓库
        const activeRepo = repositories.value.find(r => r.is_active)
        if (activeRepo) {
          selectedRepoId.value = activeRepo.id
        } else if (repositories.value.length > 0) {
          selectedRepoId.value = repositories.value[0].id
        }
      }
    } else {
      console.error('加载仓库失败:', data)
      ElMessage.error('加载仓库列表失败')
    }
  } catch (error) {
    console.error('加载仓库列表失败:', error)
    const errorMsg = error.response?.data?.error || error.message || '加载仓库列表失败'
    ElMessage.error(errorMsg)
  } finally {
    loading.value = false
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
    console.error('切换仓库失败:', error)
    ElMessage.error('切换仓库失败')
  }
}

// 导出方法供父组件调用
defineExpose({
  loadRepositories
})

onMounted(() => {
  loadRepositories()
})
</script>

<style scoped>
.repository-selector {
  display: flex;
  gap: 10px;
  align-items: center;
}

.repo-select {
  min-width: 250px;
}

.repo-option {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.active-icon {
  color: #67c23a;
  font-size: 16px;
}

.file-count {
  margin-left: auto;
}
</style>

