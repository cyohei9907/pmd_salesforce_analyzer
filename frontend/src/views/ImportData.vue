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
            <!-- 导入目录 -->
            <el-tab-pane :label="$t('import.importDirectory')" name="directory">
              <el-form :model="directoryForm" label-width="100px">
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
              <el-form :model="fileForm" label-width="100px">
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
import { Upload, Refresh, Delete } from '@element-plus/icons-vue'

const { t, locale } = useI18n()
const activeTab = ref('directory')
const importing = ref(false)
const importResult = ref(null)
const importedFiles = ref([])

const directoryForm = ref({
  path: ''
})

const fileForm = ref({
  path: ''
})

const useDefaultPath = () => {
  directoryForm.value.path = 'D:\\workspace\\project018_pmd\\pmd_analyzer\\output\\ast'
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
</style>
