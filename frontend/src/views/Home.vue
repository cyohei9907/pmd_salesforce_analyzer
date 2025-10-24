<template>
  <div class="home">
    <el-card class="welcome-card">
      <template #header>
        <div class="card-header">
          <span>{{ $t('home.welcome') }}</span>
        </div>
      </template>
      
      <div class="welcome-content">
        <h2>{{ $t('home.features') }}</h2>
        <el-divider />
        
        <el-row :gutter="20">
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header>
                <el-icon style="font-size: 32px; color: #409eff"><Upload /></el-icon>
                <h3>{{ $t('home.step1') }}</h3>
              </template>
              <p>{{ $t('home.step1Desc') }}</p>
              <el-button type="primary" @click="$router.push('/import')" style="margin-top: 10px">
                {{ $t('import.startImport') }}
              </el-button>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header>
                <el-icon style="font-size: 32px; color: #67c23a"><Share /></el-icon>
                <h3>{{ $t('home.step2') }}</h3>
              </template>
              <p>{{ $t('home.step2Desc') }}</p>
              <el-button type="success" @click="$router.push('/graph')" style="margin-top: 10px">
                {{ $t('common.view') }}
              </el-button>
            </el-card>
          </el-col>
          
          <el-col :span="8">
            <el-card shadow="hover">
              <template #header>
                <el-icon style="font-size: 32px; color: #e6a23c"><DataAnalysis /></el-icon>
                <h3>{{ $t('home.step3') }}</h3>
              </template>
              <p>{{ $t('home.step3Desc') }}</p>
              <el-button type="warning" @click="$router.push('/statistics')" style="margin-top: 10px">
                {{ $t('common.view') }}
              </el-button>
            </el-card>
          </el-col>
        </el-row>
        
        <el-divider />
        
        <div v-if="stats" class="quick-stats">
          <h3>📊 {{ $t('stats.overview') }}</h3>
          <el-row :gutter="20" style="margin-top: 20px">
            <el-col :span="6">
              <el-statistic :title="$t('stats.totalClasses')" :value="stats.classes">
                <template #prefix>
                  <el-icon><Document /></el-icon>
                </template>
              </el-statistic>
            </el-col>
            <el-col :span="6">
              <el-statistic :title="$t('stats.totalMethods')" :value="stats.methods">
                <template #prefix>
                  <el-icon><Files /></el-icon>
                </template>
              </el-statistic>
            </el-col>
            <el-col :span="6">
              <el-statistic :title="$t('stats.totalSOQL')" :value="stats.soqls">
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-statistic>
            </el-col>
            <el-col :span="6">
              <el-statistic :title="$t('stats.totalDML')" :value="stats.dmls">
                <template #prefix>
                  <el-icon><Edit /></el-icon>
                </template>
              </el-statistic>
            </el-col>
          </el-row>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/api'
import { ElMessage } from 'element-plus'

const { t } = useI18n()
const stats = ref(null)

const loadStatistics = async () => {
  try {
    stats.value = await api.getStatistics()
  } catch (error) {
    ElMessage.error(t('stats.loadError'))
  }
}

onMounted(() => {
  loadStatistics()
})
</script>

<style scoped>
.home {
  padding: 20px;
}

.welcome-card {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  font-size: 20px;
  font-weight: bold;
}

.welcome-content {
  padding: 20px;
}

.welcome-content h2 {
  margin-bottom: 10px;
}

.quick-stats {
  margin-top: 30px;
  padding: 20px;
  background-color: #f5f7fa;
  border-radius: 4px;
}
</style>
