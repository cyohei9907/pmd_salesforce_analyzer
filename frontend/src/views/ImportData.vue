<template>
  <div class="import-data">
    <el-row :gutter="20">
      <!-- 导入区域 -->
      <el-col :span="14">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>{{ $t('import.title') }}</span>
            </div>
          </template>
          
          <el-tabs v-model="activeTab">
            <!-- Git导入 -->
            <el-tab-pane name="git">
              <template #label>
                <span style="padding-right: 20px;">从Git仓库导入</span>
              </template>
              <el-form :model="gitForm" label-width="140px">
                <el-form-item label="Git仓库URL">
                  <el-input
                    v-model="gitForm.repoUrl"
                    placeholder="https://github.com/username/repo.git"
                  >
                    <template #prepend>
                      <el-icon><Link /></el-icon>
                    </template>
                  </el-input>
                </el-form-item>
                
                <el-form-item label="分支">
                  <el-input
                    v-model="gitForm.branch"
                    placeholder="main"
                  />
                </el-form-item>
                
                <el-form-item label="Apex代码路径">
                  <el-input
                    v-model="gitForm.apexDir"
                    placeholder="force-app/main/default/classes"
                    :disabled="!!detectedStructure?.apex_classes"
                  />
                  <div style="color: #909399; font-size: 12px; margin-top: 4px;">
                    {{ detectedStructure?.apex_classes ? '已自动检测' : '相对于仓库根目录的Apex类文件路径' }}
                  </div>
                </el-form-item>
                
   
                <el-form-item>
                  <el-checkbox v-model="gitForm.autoImport">分析后自动导入到图数据库</el-checkbox>
                </el-form-item>
                
                <el-form-item>
                  <el-checkbox v-model="gitForm.force">强制覆盖已存在的仓库</el-checkbox>
                </el-form-item>
                
                <el-form-item>
                  <el-button
                    type="primary"
                    @click="cloneAndAnalyze"
                    :loading="importing"
                    :icon="Download"
                  >
                    {{ importing ? '正在处理...' : '克隆并分析' }}
                  </el-button>
                  <el-button @click="clearGitForm">{{ $t('common.reset') }}</el-button>
                </el-form-item>
              </el-form>

              <!-- 项目结构检测结果 -->
              <el-alert
                v-if="detectedStructure"
                :closable="false"
                class="structure-alert"
                style="margin-bottom: 20px"
              >
                <template #title>
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <el-icon><Select /></el-icon>
                    <span>已自动检测项目结构</span>
                  </div>
                </template>
                <div style="margin-top: 10px;">
                  <div v-if="detectedStructure.apex_classes">
                    <strong>Apex类:</strong> {{ detectedStructure.apex_classes.path }} 
                    <el-tag size="small" type="success" style="margin-left: 8px;">
                      {{ detectedStructure.apex_classes.count }} 个类
                    </el-tag>
                  </div>
                  <div v-if="detectedStructure.lwc_components" style="margin-top: 8px;">
                    <strong>LWC组件:</strong> {{ detectedStructure.lwc_components.path }}
                    <el-tag size="small" type="success" style="margin-left: 8px;">
                      {{ detectedStructure.lwc_components.count }} 个组件
                    </el-tag>
                  </div>
                  <div v-if="detectedStructure.visualforce_pages" style="margin-top: 8px;">
                    <strong>Visualforce页面:</strong> {{ detectedStructure.visualforce_pages.path }}
                    <el-tag size="small" type="success" style="margin-left: 8px;">
                      {{ detectedStructure.visualforce_pages.count }} 个画面
                    </el-tag>
                  </div>
                </div>
              </el-alert>
                
              
              <!-- 进度显示 -->
              <el-alert
                v-if="analysisProgress.stage"
                :closable="false"
                class="progress-alert"
                style="margin-top: 20px; margin-bottom: 20px"
              >
                <template #title>
                  <div style="display: flex; align-items: center; gap: 8px;">
                    <el-icon class="is-loading"><Loading /></el-icon>
                    <span>{{ analysisProgress.message }}</span>
                  </div>
                </template>
                <div style="margin-top: 10px;">
                  <el-progress 
                    :percentage="analysisProgress.progress" 
                    :status="analysisProgress.stage === 'error' ? 'exception' : undefined"
                  />
                  <div style="margin-top: 8px; font-size: 12px; color: #303133;">
                    阶段: {{ analysisProgress.stage }} 
                    <span v-if="analysisProgress.total > 0">
                      ({{ analysisProgress.current }} / {{ analysisProgress.total }})
                    </span>
                  </div>
                </div>
              </el-alert>
              
              <el-alert
                v-if="gitResult"
                :title="gitResult.success ? '处理成功' : '处理失败'"
                :type="gitResult.success ? 'success' : 'error'"
                :closable="false"
                class="custom-alert"
                style="margin-top: 20px"
              >
                <div v-if="gitResult.success" class="alert-content">
                  <h4>克隆结果:</h4>
                  <p>仓库: {{ gitResult.clone?.repo_name }}</p>
                  
                  <h4 style="margin-top: 10px">分析结果:</h4>
                  <p>总文件数: {{ gitResult.analyze?.total_files }}</p>
                  <p>成功分析: {{ gitResult.analyze?.analyzed }}</p>
                  <p>失败: {{ gitResult.analyze?.failed }}</p>
                  
                  <div v-if="gitResult.import">
                    <h4 style="margin-top: 10px">导入结果:</h4>
                    <p>成功导入: {{ gitResult.import?.successful }}</p>
                    <p>失败: {{ gitResult.import?.failed }}</p>
                  </div>
                </div>
                <div v-else class="alert-content">
                  <p>{{ gitResult.error || gitResult.clone?.error || gitResult.analyze?.error }}</p>
                </div>
              </el-alert>
            </el-tab-pane>
            
            <!-- 导入目录 -->
            <el-tab-pane :label="$t('import.importDirectory')" name="directory">
              <el-form :model="directoryForm" label-width="140px">
                <el-form-item :label="$t('import.directoryPath')">
                  <el-input
                    v-model="directoryForm.path"
                    :placeholder="$t('import.selectDirectory')"
                  >
                    <template #append>
                      <el-button @click="useDefaultPath">{{ $t('common.reset') }}</el-button>
                    </template>
                  </el-input>
                </el-form-item>
                
                <el-form-item>
                  <el-button
                    type="primary"
                    @click="importDirectory"
                    :loading="importing"
                    :icon="Upload"
                  >
                    {{ importing ? $t('import.importing') : $t('import.startImport') }}
                  </el-button>
                  <el-button @click="clearForm">{{ $t('common.reset') }}</el-button>
                </el-form-item>
              </el-form>
              
              <el-alert
                v-if="importResult"
                :title="importResult.success ? $t('import.importSuccess') : $t('import.importError')"
                :type="importResult.success ? 'success' : 'error'"
                :closable="false"
                style="margin-top: 20px"
              >
                <template v-if="importResult.success">
                  <p>{{ $t('common.total') }}: {{ importResult.total }}</p>
                  <p>{{ $t('common.success') }}: {{ importResult.successful }}</p>
                  <p>{{ $t('common.error') }}: {{ importResult.failed }}</p>
                </template>
                <template v-else>
                  <p>{{ importResult.error }}</p>
                </template>
              </el-alert>
              
              <div v-if="importResult && importResult.results" style="margin-top: 20px">
                <h4>{{ $t('import.importedFiles') }}:</h4>
                <el-table :data="importResult.results" border style="margin-top: 10px">
                  <el-table-column prop="filename" :label="$t('import.fileName')" />
                  <el-table-column prop="class_name" :label="$t('graph.className')" />
                  <el-table-column prop="methods_count" :label="$t('stats.totalMethods')" width="100" />
                  <el-table-column :label="$t('common.status')" width="100">
                    <template #default="scope">
                      <el-tag :type="scope.row.success ? 'success' : 'danger'">
                        {{ scope.row.success ? $t('common.success') : $t('common.error') }}
                      </el-tag>
                    </template>
                  </el-table-column>
                </el-table>
              </div>
            </el-tab-pane>
            
            <!-- 导入单个文件 -->
            <el-tab-pane :label="$t('import.importFile')" name="file">
              <el-form :model="fileForm" label-width="140px">
                <el-form-item :label="$t('import.filePath')">
                  <el-input
                    v-model="fileForm.path"
                    :placeholder="$t('import.selectFile')"
                  />
                </el-form-item>
                
                <el-form-item>
                  <el-button
                    type="primary"
                    @click="importFile"
                    :loading="importing"
                    :icon="Upload"
                  >
                    {{ $t('import.startImport') }}
                  </el-button>
                </el-form-item>
              </el-form>
            </el-tab-pane>
          </el-tabs>
        </el-card>
      </el-col>
      
      <!-- 已导入文件列表 -->
      <el-col :span="10">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>{{ $t('import.importedFiles') }}</span>
              <el-button @click="loadImportedFiles" :icon="Refresh" size="small">{{ $t('common.refresh') }}</el-button>
            </div>
          </template>
          
          <!-- 按仓库分组显示 -->
          <div v-if="filesByRepository && filesByRepository.repositories && filesByRepository.repositories.length > 0" style="max-height: 600px; overflow-y: auto;">
            <el-collapse v-model="expandedRepos">
              <el-collapse-item 
                v-for="repo in filesByRepository.repositories" 
                :key="repo.id"
                :name="repo.id"
              >
                <template #title>
                  <div style="display: flex; align-items: center; gap: 8px; width: 100%;">
                    <el-icon><FolderOpened /></el-icon>
                    <strong>{{ repo.name }}</strong>
                    <el-tag v-if="repo.is_active" type="success" size="small">活动</el-tag>
                    <span style="margin-left: auto; font-size: 12px; color: #909399;">
                      {{ getTotalFileCount(repo) }} 个文件
                    </span>
                  </div>
                </template>
                
                <!-- Apex -->
                <div v-if="repo.components.apex && repo.components.apex.length > 0" style="margin-bottom: 15px;">
                  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
                    <el-icon color="#409eff"><Document /></el-icon>
                    <strong style="color: #409eff;">Apex Classes</strong>
                    <el-tag size="small" type="primary">{{ repo.components.apex.length }}</el-tag>
                  </div>
                  <div style="margin-left: 20px;">
                    <div v-for="file in repo.components.apex" :key="file.name" class="file-item">
                      <el-icon><Document /></el-icon>
                      <span>{{ file.name }}</span>
                      <el-tag size="small" style="margin-left: 8px;">XML</el-tag>
                    </div>
                  </div>
                </div>
                
                <!-- Visualforce -->
                <div v-if="repo.components.visualforce && repo.components.visualforce.length > 0" style="margin-bottom: 15px;">
                  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
                    <el-icon color="#e6a23c"><Document /></el-icon>
                    <strong style="color: #e6a23c;">Visualforce Pages</strong>
                    <el-tag size="small" type="warning">{{ repo.components.visualforce.length }}</el-tag>
                  </div>
                  <div style="margin-left: 20px;">
                    <div v-for="file in repo.components.visualforce" :key="file.name" class="file-item">
                      <el-icon><Document /></el-icon>
                      <span>{{ file.name }}</span>
                      <el-tag size="small" style="margin-left: 8px;">XML</el-tag>
                    </div>
                  </div>
                </div>
                
                <!-- LWC -->
                <div v-if="repo.components.lwc && repo.components.lwc.length > 0">
                  <div style="display: flex; align-items: center; gap: 6px; margin-bottom: 8px;">
                    <el-icon color="#67c23a"><Files /></el-icon>
                    <strong style="color: #67c23a;">LWC Components</strong>
                    <el-tag size="small" type="success">{{ repo.components.lwc.length }}</el-tag>
                  </div>
                  <div style="margin-left: 20px;">
                    <div v-for="file in repo.components.lwc" :key="file.name" class="file-item">
                      <el-icon><Files /></el-icon>
                      <span>{{ file.name }}</span>
                      <el-tag v-if="file.ast_file" size="small" style="margin-left: 8px;">XML</el-tag>
                      <el-tag v-else size="small" type="info" style="margin-left: 8px;">JSON</el-tag>
                    </div>
                  </div>
                </div>
              </el-collapse-item>
            </el-collapse>
          </div>
          
          <el-empty v-else description="暂无已导入的文件" />
          
          <div style="margin-top: 20px; text-align: center">
            <el-popconfirm
              :title="$t('common.confirmDelete')"
              @confirm="clearDatabase"
            >
              <template #reference>
                <el-button type="danger" :icon="Delete">{{ $t('common.clearAll') }}</el-button>
              </template>
            </el-popconfirm>
          </div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/api'
import { ElMessage } from 'element-plus'
import { 
  Upload, 
  Refresh, 
  Delete, 
  Download, 
  Link, 
  Select, 
  Document, 
  Files, 
  FolderOpened,
  Loading
} from '@element-plus/icons-vue'

const { t, locale } = useI18n()
const activeTab = ref('git')
const importing = ref(false)
const importResult = ref(null)
const gitResult = ref(null)
const filesByRepository = ref(null)
const expandedRepos = ref([])
const detectedStructure = ref(null)

// 进度跟踪
const analysisProgress = ref({
  stage: '',
  message: '',
  progress: 0,
  current: 0,
  total: 0
})
let progressTimer = null

const directoryForm = ref({
  path: ''
})

const fileForm = ref({
  path: ''
})

const gitForm = ref({
  repoUrl: 'https://github.com/trailheadapps/dreamhouse-lwc.git',
  branch: 'main',
  apexDir: 'force-app/main/default/classes',
  autoImport: true,
  force: false
})

// 计算仓库总文件数
const getTotalFileCount = (repo) => {
  let total = 0
  if (repo.components.apex) total += repo.components.apex.length
  if (repo.components.visualforce) total += repo.components.visualforce.length
  if (repo.components.lwc) total += repo.components.lwc.length
  return total
}

const useDefaultPath = () => {
  // 使用相对路径，相对于项目根目录
  directoryForm.value.path = 'output/ast'
}

const clearForm = () => {
  directoryForm.value.path = ''
  importResult.value = null
}

const importDirectory = async () => {
  if (!directoryForm.value.path) {
    ElMessage.warning(t('import.selectDirectory'))
    return
  }
  
  importing.value = true
  importResult.value = null
  
  try {
    const result = await api.importDirectory(directoryForm.value.path)
    importResult.value = { ...result, success: true }
    ElMessage.success(t('import.importSuccess'))
    loadImportedFiles()
  } catch (error) {
    importResult.value = { success: false, error: error.message || t('import.importError') }
    ElMessage.error(t('import.importError') + ': ' + (error.message || t('common.error')))
  } finally {
    importing.value = false
  }
}

const importFile = async () => {
  if (!fileForm.value.path) {
    ElMessage.warning(t('import.selectFile'))
    return
  }
  
  importing.value = true
  
  try {
    await api.importFile(fileForm.value.path)
    ElMessage.success(t('import.importSuccess'))
    loadImportedFiles()
  } catch (error) {
    ElMessage.error(t('import.importError') + ': ' + (error.message || t('common.error')))
  } finally {
    importing.value = false
  }
}

const loadImportedFiles = async () => {
  try {
    const data = await api.getImportedFiles()
    filesByRepository.value = data
    
    // 默认展开所有仓库
    if (data.repositories && data.repositories.length > 0) {
      expandedRepos.value = data.repositories.map(r => r.id)
    }
  } catch (error) {
    console.error('Failed to load imported files:', error)
    ElMessage.error(t('import.loadError'))
  }
}

const clearGitForm = () => {
  gitForm.value = {
    repoUrl: '',
    branch: 'main',
    apexDir: 'force-app/main/default/classes',
    autoImport: true,
    force: false
  }
  gitResult.value = null
  detectedStructure.value = null
  stopPolling()
  analysisProgress.value = {
    stage: '',
    message: '',
    progress: 0,
    current: 0,
    total: 0
  }
}

// 进度轮询函数
const pollProgress = async (taskId) => {
  try {
    const response = await api.getAnalysisProgress(taskId)
    
    if (response && response.success && response.progress) {
      const progress = response.progress
      
      analysisProgress.value = {
        stage: progress.stage || '',
        message: progress.message || '',
        progress: progress.progress || 0,
        current: progress.current || 0,
        total: progress.total || 0
      }
      
      // 如果还没完成,继续轮询
      if (progress.stage !== 'completed' && progress.stage !== 'error') {
        progressTimer = setTimeout(() => pollProgress(taskId), 1000) // 每秒轮询一次
      } else {
        // 完成或错误
        importing.value = false
        
        if (progress.stage === 'completed') {
          ElMessage.success('处理完成!')
          // リロードファイルリスト
          if (gitForm.value.autoImport) {
            loadImportedFiles()
          }
        } else if (progress.stage === 'error') {
          ElMessage.error('处理失败: ' + (progress.message || '未知错误'))
        }
        
        // 2秒後にクリア
        setTimeout(() => {
          analysisProgress.value = {
            stage: '',
            message: '',
            progress: 0,
            current: 0,
            total: 0
          }
        }, 3000)
      }
    } else {
      // 進度が見つからない場合
      console.warn('Progress not found for task:', taskId)
    }
  } catch (error) {
    console.error('Failed to poll progress:', error)
    // エラーの場合も続行
    if (analysisProgress.value.stage !== 'completed' && analysisProgress.value.stage !== 'error') {
      progressTimer = setTimeout(() => pollProgress(taskId), 2000) // エラー時は2秒待つ
    }
  }
}

// 停止轮询
const stopPolling = () => {
  if (progressTimer) {
    clearTimeout(progressTimer)
    progressTimer = null
  }
}

const cloneAndAnalyze = async () => {
  if (!gitForm.value.repoUrl) {
    ElMessage.warning('请输入Git仓库URL')
    return
  }
  
  importing.value = true
  gitResult.value = null
  detectedStructure.value = null
  stopPolling() // 清除之前的轮询
  
  // 重置进度
  analysisProgress.value = {
    stage: 'init',
    message: '初始化...',
    progress: 0,
    current: 0,
    total: 0
  }
  
  try {
    const result = await api.cloneAndAnalyze(
      gitForm.value.repoUrl,
      gitForm.value.branch,
      gitForm.value.apexDir,
      gitForm.value.force,
      gitForm.value.autoImport
    )
    
    // バックグラウンドタスクが開始された
    if (result.task_id) {
      ElMessage.info('处理已开始，请稍候...')
      // 開始輪詢進度
      pollProgress(result.task_id)
    } else {
      // 古い同期レスポンスの場合
      gitResult.value = result
      
      // 保存检测到的项目结构
      if (result.structure && result.structure.success) {
        detectedStructure.value = result.structure
        
        // 如果检测到Apex路径,更新表单
        if (result.structure.apex_classes) {
          gitForm.value.apexDir = result.structure.apex_classes.path
        }
      }
      
      ElMessage.success('Git仓库处理成功!')
      if (gitForm.value.autoImport) {
        loadImportedFiles()
      }
      importing.value = false
    }
  } catch (error) {
    gitResult.value = { success: false, error: error.response?.data?.error || error.message }
    ElMessage.error('处理失败: ' + (error.response?.data?.error || error.message))
    stopPolling()
    
    // 显示错误状态
    analysisProgress.value = {
      stage: 'error',
      message: '处理失败',
      progress: 0,
      current: 0,
      total: 0
    }
    importing.value = false
  }
}

const clearDatabase = async () => {
  try {
    await api.clearDatabase()
    ElMessage.success(t('common.success'))
    importedFiles.value = []
    importResult.value = null
  } catch (error) {
    ElMessage.error(t('common.error') + ': ' + (error.message || t('common.error')))
  }
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  // 使用当前locale值,将zh-CN转换为zh,ja-JP转换为ja
  const localeCode = locale.value.split('-')[0]
  return new Date(dateStr).toLocaleString(localeCode === 'zh' ? 'zh-CN' : localeCode === 'ja' ? 'ja-JP' : 'en-US')
}

onMounted(() => {
  loadImportedFiles()
  useDefaultPath()
})
</script>

<style scoped>
.import-data {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* 自定义Alert样式 - 黑色文字，灰色背景 */
.custom-alert {
  background-color: #f5f5f5 !important;
  border-color: #d3d3d3 !important;
}

.custom-alert :deep(.el-alert__title) {
  color: #303133 !important;
  font-weight: 600;
}

.custom-alert :deep(.el-alert__description),
.custom-alert .alert-content {
  color: #303133 !important;
}

.custom-alert .alert-content h4 {
  color: #303133 !important;
  font-weight: 600;
  margin: 8px 0;
}

.custom-alert .alert-content p {
  color: #303133 !important;
  margin: 4px 0;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 4px 0;
  font-size: 13px;
  color: #606266;
}

.file-item:hover {
  background-color: #f5f7fa;
  padding-left: 4px;
  border-radius: 4px;
}

/* 进度显示Alert样式 - 灰色背景，黑色文字 */
.progress-alert {
  background-color: #f5f5f5 !important;
  border-color: #d3d3d3 !important;
}

.progress-alert :deep(.el-alert__title) {
  color: #303133 !important;
  font-weight: 600;
}

.progress-alert :deep(.el-alert__description) {
  color: #303133 !important;
}

/* 项目结构检测Alert样式 - 灰色背景，黑色文字 */
.structure-alert {
  background-color: #f5f5f5 !important;
  border-color: #d3d3d3 !important;
}

.structure-alert :deep(.el-alert__title) {
  color: #303133 !important;
  font-weight: 600;
}

.structure-alert :deep(.el-alert__description) {
  color: #303133 !important;
}

.structure-alert div {
  color: #303133 !important;
}

.structure-alert strong {
  color: #303133 !important;
}
</style>
