<template>
  <div class="statistics">
    <el-row :gutter="20">
      <!-- 统计卡片 -->
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic :title="$t('stats.totalClasses')" :value="stats.classes || 0">
            <template #prefix>
              <el-icon color="#409eff"><Document /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic :title="$t('stats.totalMethods')" :value="stats.methods || 0">
            <template #prefix>
              <el-icon color="#67c23a"><Files /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic :title="$t('stats.totalSOQL')" :value="stats.soqls || 0">
            <template #prefix>
              <el-icon color="#e6a23c"><Search /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
      
      <el-col :span="6">
        <el-card shadow="hover">
          <el-statistic :title="$t('stats.totalDML')" :value="stats.dmls || 0">
            <template #prefix>
              <el-icon color="#f56c6c"><Edit /></el-icon>
            </template>
          </el-statistic>
        </el-card>
      </el-col>
    </el-row>
    
    <!-- 详细统计表格 -->
    <el-card style="margin-top: 20px">
      <template #header>
        <div class="card-header">
          <span>{{ $t('stats.detailedStats') }}</span>
          <el-button @click="loadStatistics" :icon="Refresh" :loading="loading">
            {{ loading ? $t('stats.refreshing') : $t('common.refresh') }}
          </el-button>
        </div>
      </template>
      
      <el-descriptions :column="2" border>
        <el-descriptions-item :label="$t('stats.importedFiles')">
          {{ stats.imported_files || 0 }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('stats.totalClasses')">
          {{ stats.classes || 0 }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('stats.totalMethods')">
          {{ stats.methods || 0 }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('stats.avgMethodsPerClass')">
          {{ averageMethodsPerClass }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('stats.totalSOQL')">
          {{ stats.soqls || 0 }}
        </el-descriptions-item>
        <el-descriptions-item :label="$t('stats.totalDML')">
          {{ stats.dmls || 0 }}
        </el-descriptions-item>
      </el-descriptions>
    </el-card>
    
    <!-- 图表展示 -->
    <el-row :gutter="20" style="margin-top: 20px">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>{{ $t('stats.nodeDistribution') }}</span>
          </template>
          <div class="chart-container">
            <div class="simple-chart">
              <div
                v-for="item in chartData"
                :key="item.name"
                class="chart-bar"
                :style="{ height: getBarHeight(item.value) + 'px', backgroundColor: item.color }"
              >
                <div class="chart-label">{{ item.name }}</div>
                <div class="chart-value">{{ item.value }}</div>
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>{{ $t('stats.systemInfo') }}</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item :label="$t('stats.neo4jStatus')">
              <el-tag :type="stats.classes >= 0 ? 'success' : 'danger'">
                {{ stats.classes >= 0 ? $t('stats.connected') : $t('stats.disconnected') }}
              </el-tag>
            </el-descriptions-item>
            <el-descriptions-item :label="$t('stats.databaseType')">
              Neo4j Graph Database
            </el-descriptions-item>
            <el-descriptions-item :label="$t('stats.lastUpdate')">
              {{ lastUpdateTime }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import api from '@/api'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'

const { t } = useI18n()

const stats = ref({
  classes: 0,
  methods: 0,
  soqls: 0,
  dmls: 0,
  imported_files: 0
})

const loading = ref(false)
const lastUpdateTime = ref('')

const averageMethodsPerClass = computed(() => {
  if (stats.value.classes === 0) return '0.00'
  return (stats.value.methods / stats.value.classes).toFixed(2)
})

const chartData = computed(() => [
  { name: t('graph.apexClass'), value: stats.value.classes, color: '#409eff' },
  { name: t('graph.method'), value: stats.value.methods, color: '#67c23a' },
  { name: t('graph.soqlQuery'), value: stats.value.soqls, color: '#e6a23c' },
  { name: t('graph.dmlOperation'), value: stats.value.dmls, color: '#f56c6c' }
])

const getBarHeight = (value) => {
  const maxValue = Math.max(...chartData.value.map(item => item.value))
  if (maxValue === 0) return 0
  return (value / maxValue) * 200 + 50
}

const loadStatistics = async () => {
  loading.value = true
  try {
    stats.value = await api.getStatistics()
    lastUpdateTime.value = new Date().toLocaleString()
    ElMessage.success(t('stats.updateSuccess'))
  } catch (error) {
    ElMessage.error(t('stats.loadError'))
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStatistics()
})
</script>

<style scoped>
.statistics {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 300px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.simple-chart {
  display: flex;
  align-items: flex-end;
  justify-content: space-around;
  width: 100%;
  height: 280px;
  padding: 20px;
}

.chart-bar {
  flex: 1;
  margin: 0 10px;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: flex-end;
  transition: all 0.3s;
  position: relative;
}

.chart-bar:hover {
  transform: translateY(-5px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.chart-label {
  position: absolute;
  bottom: 10px;
  color: white;
  font-weight: bold;
  font-size: 14px;
}

.chart-value {
  position: absolute;
  top: -25px;
  font-weight: bold;
  font-size: 16px;
}
</style>
