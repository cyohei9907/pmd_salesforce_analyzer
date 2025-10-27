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
                  >
                    <template #append>
                      <el-button @click="useDefaultApexPath">重置</el-button>
                    </template>
                  </el-input>
                  <div style="color: #909399; font-size: 12px; margin-top: 4px;">
                    相对于仓库根目录的Apex类文件路径
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
          
          <el-table :data="importedFiles" style="width: 100%" max-height="600">
            <el-table-column prop="class_name" :label="$t('graph.className')" />
            <el-table-column prop="filename" :label="$t('import.fileName')" />
            <el-table-column :label="$t('import.importTime')" width="180">
              <template #default="scope">
                {{ formatDate(scope.row.imported_at) }}
              </template>
            </el-table-column>
          </el-table>
          
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
import { Upload, Refresh, Delete, Download, Link } from '@element-plus/icons-vue'

const { t, locale } = useI18n()
const activeTab = ref('git')
const importing = ref(false)
const importResult = ref(null)
const gitResult = ref(null)
const importedFiles = ref([])

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
    importedFiles.value = await api.getImportedFiles()
  } catch (error) {
    ElMessage.error(t('import.loadError'))
  }
}

const useDefaultApexPath = () => {
  gitForm.value.apexDir = 'force-app/main/default/classes'
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
}

const cloneAndAnalyze = async () => {
  if (!gitForm.value.repoUrl) {
    ElMessage.warning('请输入Git仓库URL')
    return
  }
  
  importing.value = true
  gitResult.value = null
  
  try {
    const result = await api.cloneAndAnalyze(
      gitForm.value.repoUrl,
      gitForm.value.branch,
      gitForm.value.apexDir,
      gitForm.value.force,
      gitForm.value.autoImport
    )
    gitResult.value = result
    ElMessage.success('Git仓库处理成功！')
    if (gitForm.value.autoImport) {
      loadImportedFiles()
    }
  } catch (error) {
    gitResult.value = { success: false, error: error.response?.data?.error || error.message }
    ElMessage.error('处理失败: ' + (error.response?.data?.error || error.message))
  } finally {
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
</style>
