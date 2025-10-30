<template>
  <div class="graph-view">
    <!-- 顶部工具栏 -->
    <div class="toolbar">
      <!-- 仓库选择器 -->
      <RepositorySelector 
        ref="repoSelector"
        @repo-changed="handleRepoChange" 
        style="margin-right: 20px;"
      />
      
      <el-divider direction="vertical" style="height: 32px;" />
      
      <el-button @click="loadGraph" :icon="Refresh" :loading="loading">
        {{ $t('common.refresh') }}
      </el-button>
      <el-button @click="fitView" :icon="FullScreen">
        {{ $t('graph.fitView') }}
      </el-button>
      <el-button v-if="hasActiveFilter" type="info" @click="clearFilter">
        清除过滤
      </el-button>
      <el-button v-if="hasHiddenNodes" type="warning" @click="showAllNodes">
        显示全部节点
      </el-button>
      <el-button v-if="hasChainView" type="success" @click="restoreFullGraph">
        恢复完整视图
      </el-button>
    </div>

    <!-- 图表容器 -->
    <div class="graph-container" @contextmenu.prevent>
      <!-- 空数据提示 -->
      <el-empty 
        v-if="!loading && graphData && graphData.nodes.length === 0"
        description="暂无数据"
        style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); z-index: 10;"
      >
        <template #default>
          <p style="margin-bottom: 10px">数据库中没有数据，请先导入 AST 文件</p>
          <el-button type="primary" @click="$router.push('/import')">
            前往导入页面
          </el-button>
        </template>
      </el-empty>
      
      <div ref="cyContainer" class="cy-container"></div>
      
      <!-- 图例 -->
      <div class="legend">
        <h4>{{ $t('graph.legend') }}</h4>
        <div 
          class="legend-item" 
          :class="{ active: isTypeActive('ApexClass'), inactive: !isTypeActive('ApexClass') && hasActiveFilter }"
          @click="toggleNodeType('ApexClass')"
        >
          <span class="legend-color" style="background: #409eff"></span>
          <span>{{ $t('graph.apexClass') }}</span>
          <span v-if="nodeTypeCounts.ApexClass" class="count">({{ nodeTypeCounts.ApexClass }})</span>
        </div>
        <div 
          class="legend-item" 
          :class="{ active: isTypeActive('ApexMethod'), inactive: !isTypeActive('ApexMethod') && hasActiveFilter }"
          @click="toggleNodeType('ApexMethod')"
        >
          <span class="legend-color" style="background: #67c23a"></span>
          <span>{{ $t('graph.method') }}</span>
          <span v-if="nodeTypeCounts.ApexMethod" class="count">({{ nodeTypeCounts.ApexMethod }})</span>
        </div>
        <div 
          class="legend-item" 
          :class="{ active: isTypeActive('SOQLQuery'), inactive: !isTypeActive('SOQLQuery') && hasActiveFilter }"
          @click="toggleNodeType('SOQLQuery')"
        >
          <span class="legend-color" style="background: #e6a23c"></span>
          <span>{{ $t('graph.soqlQuery') }}</span>
          <span v-if="nodeTypeCounts.SOQLQuery" class="count">({{ nodeTypeCounts.SOQLQuery }})</span>
        </div>
        <div 
          class="legend-item" 
          :class="{ active: isTypeActive('DMLOperation'), inactive: !isTypeActive('DMLOperation') && hasActiveFilter }"
          @click="toggleNodeType('DMLOperation')"
        >
          <span class="legend-color" style="background: #f56c6c"></span>
          <span>{{ $t('graph.dmlOperation') }}</span>
          <span v-if="nodeTypeCounts.DMLOperation" class="count">({{ nodeTypeCounts.DMLOperation }})</span>
        </div>
        <div 
          class="legend-item" 
          :class="{ active: isTypeActive('LWCComponent'), inactive: !isTypeActive('LWCComponent') && hasActiveFilter }"
          @click="toggleNodeType('LWCComponent')"
        >
          <span class="legend-color" style="background: #9c27b0"></span>
          <span>LWC 组件</span>
          <span v-if="nodeTypeCounts.LWCComponent" class="count">({{ nodeTypeCounts.LWCComponent }})</span>
        </div>
        <div 
          class="legend-item" 
          :class="{ active: isTypeActive('JavaScriptClass'), inactive: !isTypeActive('JavaScriptClass') && hasActiveFilter }"
          @click="toggleNodeType('JavaScriptClass')"
        >
          <span class="legend-color" style="background: #795548"></span>
          <span>JS 类</span>
          <span v-if="nodeTypeCounts.JavaScriptClass" class="count">({{ nodeTypeCounts.JavaScriptClass }})</span>
        </div>
        <div 
          class="legend-item" 
          :class="{ active: isTypeActive('JavaScriptMethod'), inactive: !isTypeActive('JavaScriptMethod') && hasActiveFilter }"
          @click="toggleNodeType('JavaScriptMethod')"
        >
          <span class="legend-color" style="background: #607d8b"></span>
          <span>JS 方法</span>
          <span v-if="nodeTypeCounts.JavaScriptMethod" class="count">({{ nodeTypeCounts.JavaScriptMethod }})</span>
        </div>
        <div 
          class="legend-item" 
          :class="{ active: isTypeActive('Dependency'), inactive: !isTypeActive('Dependency') && hasActiveFilter }"
          @click="toggleNodeType('Dependency')"
        >
          <span class="legend-color" style="background: #ff9800"></span>
          <span>依赖模块</span>
          <span v-if="nodeTypeCounts.Dependency" class="count">({{ nodeTypeCounts.Dependency }})</span>
        </div>
      </div>
    </div>

    <!-- 节点详情抽屉 -->
    <el-drawer
      v-model="drawerVisible"
      :title="$t('graph.nodeDetails')"
      :size="800"
      direction="rtl"
      class="node-detail-drawer"
    >
      <div v-if="selectedNode" class="node-detail">
        <el-descriptions :column="1" border class="detail-descriptions">
          <el-descriptions-item :label="$t('graph.nodeType')">
            <el-tag :type="getNodeTypeTagColor(selectedNode.type)">
              {{ selectedNode.type }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item :label="$t('graph.nodeName')">
            <div class="detail-value">{{ selectedNode.name || selectedNode.id }}</div>
          </el-descriptions-item>
          <el-descriptions-item 
            v-for="(value, key) in selectedNode.properties" 
            :key="key"
            :label="key"
          >
            <div class="detail-value">{{ value }}</div>
          </el-descriptions-item>
        </el-descriptions>
        
        <!-- 源代码显示 -->
        <div v-if="shouldShowSourceCode(selectedNode)" class="source-code-section">
          <el-divider />
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
            <h3 style="margin: 0;">源代码</h3>
            <el-button 
              v-if="!sourceCode && !loadingSource"
              type="primary" 
              size="small"
              @click="loadSourceCodeForNode(selectedNode)"
            >
              查看源代码
            </el-button>
          </div>
          
          <div v-if="loadingSource" style="text-align: center; padding: 20px;">
            <el-icon class="is-loading" style="font-size: 32px;"><Loading /></el-icon>
            <p>加载中...</p>
          </div>
          
          <div v-else-if="sourceCode" class="code-viewer">
            <pre><code class="language-apex">{{ sourceCode }}</code></pre>
          </div>
          
          <el-empty v-else-if="sourceCodeError" :description="sourceCodeError" />
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useRouter } from 'vue-router'
import api from '@/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Refresh, FullScreen, Loading } from '@element-plus/icons-vue'
import cytoscape from 'cytoscape'
import coseBilkent from 'cytoscape-cose-bilkent'
import cxtmenu from 'cytoscape-cxtmenu'
import RepositorySelector from '@/components/RepositorySelector.vue'

// 注册布局插件和右键菜单插件
cytoscape.use(coseBilkent)
cytoscape.use(cxtmenu)

const { t } = useI18n()
const router = useRouter()

// 状态管理
const cyContainer = ref(null)
const repoSelector = ref(null)
const loading = ref(false)
const drawerVisible = ref(false)
const selectedNode = ref(null)
const graphData = ref(null)
const currentRepoId = ref(null)

// 源代码相关
const sourceCode = ref('')
const loadingSource = ref(false)
const sourceCodeError = ref('')

let cy = null // Cytoscape 实例

// 数据存储
const allNodes = ref([])
const allEdges = ref([])
const nodeTypeCounts = ref({
  ApexClass: 0,
  ApexMethod: 0,
  SOQLQuery: 0,
  DMLOperation: 0,
  LWCComponent: 0,
  JavaScriptClass: 0,
  JavaScriptMethod: 0,
  ApexClassPlaceholder: 0,
  ApexMethodPlaceholder: 0,
  Dependency: 0
})

// 过滤状态
const activeNodeTypes = ref(new Set())
const hasActiveFilter = computed(() => activeNodeTypes.value.size > 0)
const hasHiddenNodes = ref(false)
const hasChainView = ref(false) // 是否处于链路查看模式

// 工具函数
const getNodeColor = (type) => {
  const colors = {
    'ApexClass': '#409eff',
    'ApexMethod': '#67c23a',
    'SOQLQuery': '#e6a23c',
    'DMLOperation': '#f56c6c',
    'LWCComponent': '#9c27b0',
    'JavaScriptClass': '#795548',
    'JavaScriptMethod': '#607d8b',
    'ApexClassPlaceholder': '#b3d9ff',  // 淡蓝色
    'ApexMethodPlaceholder': '#c3e6cb', // 淡绿色
    'Dependency': '#ff9800', // 橙色
  }
  return colors[type] || '#909399'
}

const getNodeTypeTagColor = (type) => {
  const colors = {
    'ApexClass': 'primary',
    'ApexMethod': 'success',
    'SOQLQuery': 'warning',
    'DMLOperation': 'danger',
    'LWCComponent': 'primary',
    'JavaScriptClass': 'warning',
    'JavaScriptMethod': 'info',
    'Dependency': 'warning' 
  }
  return colors[type] || 'info'
}

const isTypeActive = (type) => {
  if (activeNodeTypes.value.size === 0) return true
  return activeNodeTypes.value.has(type)
}

// 判断是否应该显示源代码
const shouldShowSourceCode = (node) => {
  if (!node) return false
  return ['ApexClass', 'ApexMethod', 'SOQLQuery', 'DMLOperation', 'LWCComponent', 'JavaScriptClass', 'JavaScriptMethod'].includes(node.type)
}

// 根据节点类型加载源代码
const loadSourceCodeForNode = async (node) => {
  if (!node) return
  
  let className = ''
  
  // 根据节点类型获取类名
  if (node.type === 'ApexClass') {
    className = node.name || node.id
  } else if (node.type === 'ApexMethod') {
    className = node.properties?.className || ''
  } else if (node.type === 'SOQLQuery' || node.type === 'DMLOperation') {
    className = node.properties?.className || ''
  } else if (node.type === 'LWCComponent') {
    className = node.name || node.id
  } else if (node.type === 'JavaScriptClass') {
    className = node.properties?.componentName || node.name || ''
  } else if (node.type === 'JavaScriptMethod') {
    className = node.properties?.componentName || ''
  }
  
  if (!className) {
    sourceCodeError.value = '无法获取类名'
    return
  }
  
  await loadSourceCode(className)
}

// 加载源代码
const loadSourceCode = async (className) => {
  loadingSource.value = true
  sourceCode.value = ''
  sourceCodeError.value = ''
  
  try {
    const result = await api.getSourceCode(className)
    if (result.success) {
      sourceCode.value = result.source_code
    } else {
      sourceCodeError.value = result.error || '加载失败'
    }
  } catch (error) {
    console.error('Failed to load source code:', error)
    sourceCodeError.value = error.message || '加载失败'
  } finally {
    loadingSource.value = false
  }
}

// 应用布局并添加动画
const applyLayoutWithAnimation = () => {
  cy.nodes().forEach((node, index) => {
    node.style('opacity', 0)
    setTimeout(() => {
      node.animate({
        style: { opacity: 1 },
        duration: 500,
        easing: 'ease-in-out-cubic'
      })
    }, index * 20)
  })
  
  cy.edges().forEach((edge, index) => {
    edge.style('opacity', 0)
    setTimeout(() => {
      edge.animate({
        style: { opacity: 1 },
        duration: 500,
        easing: 'ease-in-out-cubic'
      })
    }, cy.nodes().length * 20 + index * 10)
  })
  
  const layout = cy.layout({
    name: 'cose',
    animate: true,
    animationDuration: 1000,
    animationEasing: 'ease-out-cubic',
    fit: true,
    padding: 50,
    nodeRepulsion: 8000,
    idealEdgeLength: 100,
    edgeElasticity: 100,
    nestingFactor: 1.2,
    gravity: 0.8,
    numIter: 1000,
    initialTemp: 200,
    coolingFactor: 0.95,
    minTemp: 1
  })
  
  layout.run()
  
  // 布局完成后保存位置
  layout.on('layoutstop', () => {
    // レイアウト保存機能は現在無効化（マルチリポジトリ対応が必要）
    // saveGraphLayout()
  })
}

// 保存图布局和完整数据
// TODO: マルチリポジトリ対応のレイアウト保存機能を実装
const saveGraphLayout = async () => {
  if (!cy) return
  
  try {
    // 保存节点位置
    const layout = {}
    cy.nodes().forEach(node => {
      layout[node.id()] = node.position()
    })
    
    // 保存完整的图数据（包括节点和边）
    const graphSnapshot = {
      layout: layout,
      nodes: allNodes.value,
      edges: allEdges.value,
      timestamp: new Date().toISOString(),
      repositoryId: currentRepoId.value // リポジトリIDを追加
    }
    
    // マルチリポジトリ対応が必要なため、現在は無効化
    // await api.saveGraphLayout(graphSnapshot)
    console.log('Graph layout save is currently disabled (multi-repository support needed)')
  } catch (error) {
    console.error('Failed to save graph layout:', error)
  }
}

// 处理仓库切换
const handleRepoChange = async (repoId) => {
  console.log('Repository changed to:', repoId)
  currentRepoId.value = repoId
  // 重新加载图数据
  await loadGraph(true)
}

// 加载图数据
const loadGraph = async (showMessage = true) => {
  loading.value = true
  try {
    // 如果有选中的仓库,加载该仓库的数据
    let apiEndpoint = '/graph/'
    if (currentRepoId.value) {
      apiEndpoint = `/repositories/${currentRepoId.value}/graph/`
    } else {
      // 没有选中仓库,检查是否有可用的仓库
      try {
        const reposData = await api.get('/repositories/')
        if (reposData.success && reposData.repositories.length === 0) {
          console.log('No repositories available')
          graphData.value = { nodes: [], edges: [] }
          loading.value = false
          return
        }
      } catch (error) {
        console.error('Failed to check repositories:', error)
      }
    }
    
    // レイアウト読み込み機能は現在無効化（マルチリポジトリ対応が必要）
    // 先尝试加载保存的快照
    let nodes = []
    let edges = []
    let savedLayout = null
    let useSnapshot = false
    
    // レイアウトスナップショット機能は無効化
    // try {
    //   const layoutResponse = await api.loadGraphLayout()
    //   if (layoutResponse.success && layoutResponse.layout) {
    //     const snapshot = layoutResponse.layout
    //     
    //     if (snapshot.nodes && snapshot.edges && snapshot.layout) {
    //       console.log('Loading from saved snapshot...')
    //       nodes = snapshot.nodes
    //       edges = snapshot.edges
    //       savedLayout = snapshot.layout
    //       useSnapshot = true
    //       
    //       nodeTypeCounts.value = {
    //         ApexClass: 0,
    //         ApexMethod: 0,
    //         SOQLQuery: 0,
    //         DMLOperation: 0
    //       }
    //       for (const node of nodes) {
    //         const type = node.data.type
    //         if (nodeTypeCounts.value.hasOwnProperty(type)) {
    //           nodeTypeCounts.value[type]++
    //         }
    //       }
    //     } else if (snapshot.layout) {
    //       savedLayout = snapshot.layout || snapshot
    //     }
    //   }
    // } catch (error) {
    //   console.log('No saved snapshot found, loading from backend...')
    // }
    
    // 如果没有快照，从后端加载
    if (!useSnapshot) {
      let data
      if (currentRepoId.value) {
        // 加载指定仓库的图数据
        const responseData = await api.get(apiEndpoint)
        data = responseData.graph || responseData
      } else {
        // 加载所有图数据
        data = await api.getGraphData()
      }
      graphData.value = data
      
      // DEBUG: Log API response data
      console.log('Graph API Response:', {
        totalNodes: data.nodes?.length,
        totalEdges: data.edges?.length,
        nodeTypes: data.nodes?.reduce((acc, node) => {
          acc[node.type] = (acc[node.type] || 0) + 1
          return acc
        }, {}),
        sampleNodes: data.nodes?.slice(0, 5)
      })
      
      // 转换节点数据
      nodes = data.nodes.map(node => ({
        data: {
          id: String(node.id),
          label: node.type === 'SOQLQuery' ? 'SOQL' : (node.name || node.id),
          type: node.type,
          color: getNodeColor(node.type),
          properties: node.properties || {},
          originalData: node
        }
      }))
      
      // 统计节点类型
      nodeTypeCounts.value = {
        ApexClass: 0,
        ApexMethod: 0,
        SOQLQuery: 0,
        DMLOperation: 0,
        LWCComponent: 0,
        JavaScriptClass: 0,
        JavaScriptMethod: 0,
        ApexClassPlaceholder: 0,
        ApexMethodPlaceholder: 0,
        Dependency: 0
      }
      for (const node of nodes) {
        const type = node.data.type
        if (nodeTypeCounts.value.hasOwnProperty(type)) {
          nodeTypeCounts.value[type]++
        }
      }
      
      // 转换边数据
      const validNodeIds = new Set(nodes.map(n => n.data.id))
      edges = data.edges
        .filter(edge => {
          const source = String(edge.source)
          const target = String(edge.target)
          return validNodeIds.has(source) && validNodeIds.has(target)
        })
        .map((edge, index) => ({
          data: {
            id: `edge-${index}`,
            source: String(edge.source),
            target: String(edge.target),
            label: edge.label || edge.type
          }
        }))
    }
    
    // 保存原始数据
    allNodes.value = nodes
    allEdges.value = edges
    
    console.log('Loaded:', nodes.length, 'nodes,', edges.length, 'edges')
    
    // 创建或更新图
    if (cy) {
      cy.elements().remove()
      cy.add(nodes)
      cy.add(edges)
      
      // 如果有保存的布局，应用它
      if (savedLayout) {
        console.log('Applying saved layout...')
        
        // 应用保存的位置
        cy.nodes().forEach(node => {
          const nodeId = node.id()
          if (savedLayout[nodeId]) {
            node.position(savedLayout[nodeId])
          }
        })
        
        // 添加淡入动画
        cy.nodes().forEach((node, index) => {
          node.style('opacity', 0)
          setTimeout(() => {
            node.animate({
              style: { opacity: 1 },
              duration: 500,
              easing: 'ease-in-out-cubic'
            })
          }, index * 20)
        })
        
        cy.edges().forEach((edge, index) => {
          edge.style('opacity', 0)
          setTimeout(() => {
            edge.animate({
              style: { opacity: 1 },
              duration: 500,
              easing: 'ease-in-out-cubic'
            })
          }, cy.nodes().length * 20 + index * 10)
        })
        
        // 适应视图
        setTimeout(() => {
          cy.fit(null, 50)
        }, 600)
      } else {
        // 没有保存的布局，使用自动布局
        applyLayoutWithAnimation()
      }
    } else {
      initCytoscape(nodes, edges)
    }
    
    if (showMessage) {
      ElMessage.success(t('graph.loadSuccess'))
    }
  } catch (error) {
    console.error('Load graph error:', error)
    ElMessage.error(t('graph.loadError'))
  } finally {
    loading.value = false
  }
}

// 初始化 Cytoscape
const initCytoscape = (nodes, edges) => {
  cy = cytoscape({
    container: cyContainer.value,
    
    elements: {
      nodes: nodes,
      edges: edges
    },
    
    style: [
      {
        selector: 'node',
        style: {
          'background-color': 'data(color)',
          'label': 'data(label)',
          'text-valign': 'center',
          'text-halign': 'center',
          'font-size': '16px',
          'width': '120px',       
          'height': '120px',      
          'color': '#333',
          'text-outline-width': 2,
          'text-outline-color': '#fff',
          'transition-property': 'background-color, border-color, border-width, opacity',
          'transition-duration': '0.3s',
          'transition-timing-function': 'ease-in-out'
        }
      },
      // LWC组件节点 - 更大尺寸
      {
        selector: 'node[type = "LWCComponent"]',
        style: {
          'width': '140px',
          'height': '140px',
          'font-size': '18px',
          'border-width': '3px',
          'border-color': '#4CAF50',
          'border-style': 'solid'
        }
      },
      // JavaScript类节点
      {
        selector: 'node[type = "JavaScriptClass"]',
        style: {
          'width': '130px',
          'height': '130px',
          'font-size': '17px',
          'border-width': '2px',
          'border-color': '#FF9800',
          'border-style': 'solid'
        }
      },
      // JavaScript方法节点
      {
        selector: 'node[type = "JavaScriptMethod"]',
        style: {
          'width': '110px',
          'height': '110px',
          'font-size': '15px'
        }
      },
      // Apex类节点
      {
        selector: 'node[type = "ApexClass"]',
        style: {
          'width': '125px',
          'height': '125px',
          'font-size': '16px',
          'border-width': '2px',
          'border-color': '#2196F3',
          'border-style': 'solid'
        }
      },
      // DML操作节点 - 小一些
      {
        selector: 'node[type = "DMLOperation"]',
        style: {
          'width': '90px',
          'height': '90px',
          'font-size': '14px',
          'shape': 'diamond'
        }
      },
      // SOQL查询节点 - 小一些
      {
        selector: 'node[type = "SOQLQuery"]',
        style: {
          'width': '95px',
          'height': '95px',
          'font-size': '14px',
          'shape': 'hexagon'
        }
      },
      {
        selector: 'node:active',
        style: {
          'overlay-opacity': 0.2,
          'overlay-color': '#000'
        }
      },
      {
        selector: 'edge',
        style: {
          'width': 2,
          'line-color': '#999',
          'target-arrow-color': '#999',
          'target-arrow-shape': 'triangle',
          'curve-style': 'bezier',
          'label': 'data(label)',
          'font-size': '10px',
          'color': '#666',
          'text-background-color': '#fff',
          'text-background-opacity': 0.8,
          'text-background-padding': '2px',
          'transition-property': 'line-color, target-arrow-color, width, opacity',
          'transition-duration': '0.3s',
          'transition-timing-function': 'ease-in-out'
        }
      },
      {
        selector: ':selected',
        style: {
          'border-width': 3,
          'border-color': '#000'
        }
      },
      {
        selector: '.highlighted',
        style: {
          'border-width': 3,
          'border-color': '#FF0000',
          'line-color': '#FF0000',
          'target-arrow-color': '#FF0000',
          'z-index': 999
        }
      },
      {
        selector: '.filtered',
        style: {
          'opacity': 0.2
        }
      }
    ],
    
    layout: {
      name: 'cose-bilkent',  // 使用更高级的cose-bilkent布局,更好的节点分布
      animate: true,
      animationDuration: 1500,  // 增加动画时长
      animationEasing: 'ease-out-cubic',
      fit: true,
      padding: 80,
      
      // cose-bilkent特定参数
      quality: 'default',  // 'default' 或 'proof'
      nodeDimensionsIncludeLabels: true,  // 考虑标签尺寸
      randomize: false,
      
      // 节点分布参数
      nodeRepulsion: 12000,  // 增加节点斥力,特别适用于LWC密集区域
      idealEdgeLength: 150,  // 增加理想边长,让节点分布更开
      edgeElasticity: 0.45,
      nestingFactor: 0.1,
      gravity: 0.4,  // 降低重力,让节点分布更自由
      numIter: 2500,  // 增加迭代次数,获得更好的布局
      
      // 温度控制
      initialTemp: 1000,
      coolingFactor: 0.99,
      minTemp: 1.0,
      
      // 特殊设置用于处理密集区域
      gravityRangeCompound: 1.5,
      gravityCompound: 1.0,
      gravityRange: 3.8,
      
      // 使用多级布局,处理大图
      improveFlow: true,
      tile: true,  // 瓦片布局,防止重叠
      tilingPaddingVertical: 30,
      tilingPaddingHorizontal: 30
    },
    
    minZoom: 0.1,
    maxZoom: 5,              // 增大最大缩放倍数
    wheelSensitivity: 4,      // 增大滚轮灵敏度到4 (原来2的2倍)
    
    // 启用拖动画面
    userPanningEnabled: true,
    panningEnabled: true,
    
    // 禁用默认的用户交互行为
    autoungrabify: false,
    autounselectify: false
  })
  
  // 实现右键拖动画面功能
  let isPanning = false
  let panStartPos = null
  
  cy.on('mousedown', function(event) {
    if (event.originalEvent && event.originalEvent.button === 2) {
      // 右键点击且不在节点上
      if (!event.target || event.target === cy) {
        isPanning = true
        panStartPos = { x: event.originalEvent.clientX, y: event.originalEvent.clientY }
        event.originalEvent.preventDefault()
      }
    }
  })
  
  cy.on('mousemove', function(event) {
    if (isPanning && panStartPos) {
      const deltaX = event.originalEvent.clientX - panStartPos.x
      const deltaY = event.originalEvent.clientY - panStartPos.y
      
      const pan = cy.pan()
      cy.pan({
        x: pan.x + deltaX,
        y: pan.y + deltaY
      })
      
      panStartPos = { x: event.originalEvent.clientX, y: event.originalEvent.clientY }
      event.originalEvent.preventDefault()
    }
  })
  
  cy.on('mouseup', function(event) {
    if (event.originalEvent && event.originalEvent.button === 2) {
      isPanning = false
      panStartPos = null
    }
  })
  
  // 节点拖动结束后保存布局（現在無効化）
  cy.on('dragfree', 'node', () => {
    // レイアウト保存は現在無効化（マルチリポジトリ対応が必要）
    // if (window.saveLayoutTimeout) {
    //   clearTimeout(window.saveLayoutTimeout)
    // }
    // window.saveLayoutTimeout = setTimeout(() => {
    //   saveGraphLayout()
    // }, 1000)
  })
  
  // 立即阻止容器的右键菜单
  const container = cy.container()
  if (container) {
    // 阻止所有的 contextmenu 事件
    const preventContext = (e) => {
      e.preventDefault()
      e.stopPropagation()
      return false
    }
    container.addEventListener('contextmenu', preventContext, { capture: true })
    
    // 同时监听 mouseup 事件,在右键松开时也阻止
    container.addEventListener('mouseup', (e) => {
      if (e.button === 2) { // 右键
        e.preventDefault()
        e.stopPropagation()
      }
    }, { capture: true })
  }
  
  // 初始化右键菜单插件
  cy.cxtmenu({
    selector: 'node',
    commands: [
      {
        content: `<span style="display: flex; align-items: center; gap: 8px;"><svg style="width: 16px; height: 16px;" fill="currentColor" viewBox="0 0 1024 1024"><path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm0 820c-205.4 0-372-166.6-372-372s166.6-372 372-372 372 166.6 372 372-166.6 372-372 372z"/><path d="M464 336a48 48 0 1 0 96 0 48 48 0 1 0-96 0zm72 112h-48c-4.4 0-8 3.6-8 8v272c0 4.4 3.6 8 8 8h48c4.4 0 8-3.6 8-8V456c0-4.4-3.6-8-8-8z"/></svg>${t('graph.viewDetails')}</span>`,
        select: function(ele) {
          selectedNode.value = ele.data('originalData')
          // 重置源代码状态
          sourceCode.value = ''
          loadingSource.value = false
          sourceCodeError.value = ''
          drawerVisible.value = true
        }
      },
      {
        content: `<span style="display: flex; align-items: center; gap: 8px;"><svg style="width: 16px; height: 16px;" fill="currentColor" viewBox="0 0 1024 1024"><path d="M512 64C264.6 64 64 264.6 64 512s200.6 448 448 448 448-200.6 448-448S759.4 64 512 64zm192 472c0 4.4-3.6 8-8 8H544v152c0 4.4-3.6 8-8 8h-48c-4.4 0-8-3.6-8-8V544H328c-4.4 0-8-3.6-8-8v-48c0-4.4 3.6-8 8-8h152V328c0-4.4 3.6-8 8-8h48c4.4 0 8 3.6 8 8v152h152c4.4 0 8 3.6 8 8v48z"/></svg>仅显示关联节点</span>`,
        select: function(ele) {
          showOnlyRelatedNodes(ele)
        }
      },
      {
        content: `<span style="display: flex; align-items: center; gap: 8px;"><svg style="width: 16px; height: 16px;" fill="currentColor" viewBox="0 0 1024 1024"><path d="M877.5 810.3L646.2 579c24.4-39.8 38.4-86.4 38.4-136C684.6 336.1 598.5 250 492.6 250S300.6 336.1 300.6 443s86.1 193 192 193c49.6 0 96.2-14 136-38.4l231.3 231.3c12.5 12.5 32.8 12.5 45.3 0l2.3-2.3c12.5-12.5 12.5-32.8 0-45.3zM492.6 584c-77.8 0-141-63.2-141-141s63.2-141 141-141 141 63.2 141 141-63.2 141-141 141z"/></svg>查询DML调用来源</span>`,
        select: function(ele) {
          findDMLCallers(ele)
        },
        show: function(ele) {
          // 只对DML节点显示此菜单项
          const nodeType = ele.data('originalData')?.type
          return nodeType === 'DMLOperation'
        }
      }
    ],
    fillColor: 'rgba(255, 255, 255, 0.95)',
    activeFillColor: 'rgba(245, 247, 250, 1)',
    activePadding: 8,
    indicatorSize: 20,
    separatorWidth: 3,
    spotlightPadding: 4,
    adaptativeNodeSpotlightRadius: true,
    minSpotlightRadius: 20,
    maxSpotlightRadius: 40,
    openMenuEvents: 'cxttapstart',
    itemColor: '#606266',
    itemTextShadowColor: 'transparent',
    zIndex: 9999,
    atMouse: false,
    // 尝试设置 spotlight 颜色为白色
    outsideMenuCancel: 10
  })
  
  // 使用 MutationObserver 监听 spotlight 元素的创建并修改其样式
  const observer = new MutationObserver(() => {
    const spotlight = document.querySelector('#cy-cxtmenu-spotlight circle')
    if (spotlight) {
      spotlight.setAttribute('stroke', 'white')
      spotlight.setAttribute('stroke-width', '3')
      spotlight.setAttribute('fill', 'none')
    }
  })
  
  // 监听 cytoscape 容器的变化
  if (cyContainer.value) {
    observer.observe(cyContainer.value, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['stroke', 'stroke-width']
    })
  }
  
  // 添加初始化动画效果
  cy.nodes().forEach((node, index) => {
    // 初始设置节点为不可见
    node.style('opacity', 0)
    
    // 延迟显示每个节点，创建渐进效果
    setTimeout(() => {
      node.animate({
        style: { opacity: 1 },
        duration: 500,
        easing: 'ease-in-out-cubic'
      })
    }, index * 20) // 每个节点延迟20ms
  })
  
  // 边也添加淡入效果
  cy.edges().forEach((edge, index) => {
    edge.style('opacity', 0)
    setTimeout(() => {
      edge.animate({
        style: { opacity: 1 },
        duration: 500,
        easing: 'ease-in-out-cubic'
      })
    }, cy.nodes().length * 20 + index * 10) // 在节点动画后开始
  })
  
  console.log('Cytoscape initialized:', cy.nodes().length, 'nodes')
}

// 显示仅与选中节点相关的节点（包括所有关联链路）
const showOnlyRelatedNodes = (node) => {
  if (!cy) return
  
  // 使用广度优先搜索找到所有连接的节点
  const relatedNodeIds = new Set()
  const visited = new Set()
  const queue = [node]
  
  while (queue.length > 0) {
    const currentNode = queue.shift()
    const currentId = currentNode.id()
    
    if (visited.has(currentId)) continue
    visited.add(currentId)
    relatedNodeIds.add(currentId)
    
    // 获取所有连接的节点（入边和出边）
    const connectedNodes = currentNode.neighborhood('node')
    for (const n of connectedNodes) {
      if (!visited.has(n.id())) {
        queue.push(n)
      }
    }
  }
  
  // 隐藏所有不相关的节点和边
  for (const ele of cy.elements()) {
    if (ele.isNode()) {
      if (relatedNodeIds.has(ele.id())) {
        ele.style('display', 'element')
      } else {
        ele.style('display', 'none')
      }
    } else if (ele.isEdge()) {
      // 只显示连接相关节点的边
      const sourceId = ele.source().id()
      const targetId = ele.target().id()
      if (relatedNodeIds.has(sourceId) && relatedNodeIds.has(targetId)) {
        ele.style('display', 'element')
      } else {
        ele.style('display', 'none')
      }
    }
  }
  
  hasHiddenNodes.value = true
  
  // 适应视图
  cy.fit(cy.elements(':visible'), 50)
}

// 显示所有节点
const showAllNodes = () => {
  if (!cy) return
  
  // 显示所有元素
  for (const ele of cy.elements()) {
    ele.style('display', 'element')
  }
  
  hasHiddenNodes.value = false
  
  // 适应视图
  cy.fit(null, 50)
}

// DML调用来源查询 - 显示完整调用链路
const findDMLCallers = (dmlNode) => {
  if (!cy || !dmlNode) return
  
  const dmlId = dmlNode.id()
  const dmlData = dmlNode.data('originalData') || dmlNode.data()
  
  console.log('DML Node Data:', dmlData)
  console.log('DML Node ID:', dmlId)
  
  // 构建完整的调用链路
  const callChains = buildCallChains(dmlId)
  
  if (callChains.length > 0) {
    const operationType = dmlData?.operationType || 'Unknown'
    const className = dmlData?.className || 'Unknown'
    const methodName = dmlData?.methodName || 'Unknown'
    
    let message = `DML操作信息:\n`
    message += `  类型: ${operationType}\n`
    message += `  所属类: ${className}\n`
    message += `  所属方法: ${methodName}\n\n`
    
    if (callChains.length === 1) {
      // 只有一条链路，直接显示并高亮
      message += `调用链路:\n\n`
      const chain = callChains[0]
      chain.forEach((node, nodeIndex) => {
        const indent = '  '.repeat(nodeIndex)
        const arrow = nodeIndex > 0 ? ' → ' : ''
        message += `${indent}${arrow}${node.name} (${node.type})\n`
      })
      
      ElMessageBox.alert(message, 'DML调用链路分析', {
        confirmButtonText: '高亮显示链路',
        cancelButtonText: '关闭',
        showCancelButton: true,
        type: 'info',
        customClass: 'dml-callers-dialog'
      }).then(() => {
        highlightSingleCallChain(dmlNode, chain)
      }).catch(() => {
        // 用户点击关闭，不做任何操作
      })
    } else {
      // 多条链路，让用户选择
      message += `发现 ${callChains.length} 条调用链路，请选择要查看的链路:\n\n`
      
      callChains.forEach((chain, chainIndex) => {
        const rootNode = chain[chain.length - 1] // 链路的根节点
        message += `${chainIndex + 1}. 从 ${rootNode.name} (${rootNode.type}) 开始\n`
      })
      
      ElMessageBox.prompt(message, 'DML调用链路选择', {
        confirmButtonText: '查看选中链路',
        cancelButtonText: '查看所有链路',
        showCancelButton: true,
        inputPattern: /^[1-9]\d*$/,
        inputErrorMessage: `请输入 1 到 ${callChains.length} 之间的数字`,
        inputPlaceholder: `输入链路编号 (1-${callChains.length})`,
        type: 'info',
        customClass: 'dml-callers-dialog'
      }).then(({ value }) => {
        const chainIndex = parseInt(value) - 1
        if (chainIndex >= 0 && chainIndex < callChains.length) {
          // 显示选中的单条链路
          showSingleChainDetails(dmlNode, callChains[chainIndex], chainIndex + 1)
        }
      }).catch(() => {
        // 用户点击"查看所有链路"或关闭
        showAllChainsDetails(dmlNode, callChains)
      })
    }
  } else {
    ElMessage.info('该DML操作没有找到调用来源')
  }
}

// 显示单条链路的详细信息
const showSingleChainDetails = (dmlNode, chain, chainNumber) => {
  const dmlData = dmlNode.data('originalData') || dmlNode.data()
  const operationType = dmlData?.operationType || 'Unknown'
  const className = dmlData?.className || 'Unknown'
  const methodName = dmlData?.methodName || 'Unknown'
  
  let message = `DML操作信息:\n`
  message += `  类型: ${operationType}\n`
  message += `  所属类: ${className}\n`
  message += `  所属方法: ${methodName}\n\n`
  message += `调用链路 ${chainNumber}:\n\n`
  
  chain.forEach((node, nodeIndex) => {
    const indent = '  '.repeat(nodeIndex)
    const arrow = nodeIndex > 0 ? ' → ' : ''
    message += `${indent}${arrow}${node.name} (${node.type})\n`
  })
  
  ElMessageBox.alert(message, `DML调用链路 ${chainNumber} 详情`, {
    confirmButtonText: '高亮显示此链路',
    cancelButtonText: '关闭',
    showCancelButton: true,
    type: 'info',
    customClass: 'dml-callers-dialog'
  }).then(() => {
    highlightSingleCallChain(dmlNode, chain)
  }).catch(() => {
    // 用户点击关闭，不做任何操作
  })
}

// 显示所有链路的详细信息（原来的功能）
const showAllChainsDetails = (dmlNode, callChains) => {
  const dmlData = dmlNode.data('originalData') || dmlNode.data()
  const operationType = dmlData?.operationType || 'Unknown'
  const className = dmlData?.className || 'Unknown'
  const methodName = dmlData?.methodName || 'Unknown'
  
  let message = `DML操作信息:\n`
  message += `  类型: ${operationType}\n`
  message += `  所属类: ${className}\n`
  message += `  所属方法: ${methodName}\n\n`
  message += `所有调用链路:\n\n`
  
  callChains.forEach((chain, chainIndex) => {
    message += `链路 ${chainIndex + 1}:\n`
    chain.forEach((node, nodeIndex) => {
      const indent = '  '.repeat(nodeIndex)
      const arrow = nodeIndex > 0 ? ' → ' : ''
      message += `${indent}${arrow}${node.name} (${node.type})\n`
    })
    message += '\n'
  })
  
  ElMessageBox.alert(message, 'DML完整调用链路分析', {
    confirmButtonText: '高亮显示所有链路',
    cancelButtonText: '关闭',
    showCancelButton: true,
    type: 'info',
    customClass: 'dml-callers-dialog'
  }).then(() => {
    highlightAllCallChains(dmlNode, callChains)
  }).catch(() => {
    // 用户点击关闭，不做任何操作
  })
}

// 构建从DML节点开始的完整调用链路
const buildCallChains = (startNodeId) => {
  const chains = []
  const visited = new Set()
  
  // 递归构建调用链
  const buildChain = (nodeId, currentChain) => {
    if (visited.has(nodeId)) {
      // 避免循环引用
      return
    }
    
    const node = cy.getElementById(nodeId)
    if (!node.length) return
    
    const nodeData = node.data('originalData') || node.data()
    const chainNode = {
      id: nodeId,
      name: nodeData?.name || nodeData?.canonicalName || node.data('label') || 'Unknown',
      type: nodeData?.type || 'Unknown',
      node: node
    }
    
    const newChain = [chainNode, ...currentChain]
    
    // 查找调用此节点的边
    const incomingEdges = cy.edges().filter(edge => {
      return edge.target().id() === nodeId
    })
    
    if (incomingEdges.length === 0) {
      // 没有更多调用者，这是链路的终点
      chains.push(newChain)
    } else {
      // 继续向上追溯
      visited.add(nodeId)
      incomingEdges.forEach(edge => {
        const sourceNodeId = edge.source().id()
        buildChain(sourceNodeId, newChain)
      })
      visited.delete(nodeId)
    }
  }
  
  // 从DML节点开始构建
  const dmlNode = cy.getElementById(startNodeId)
  const dmlData = dmlNode.data('originalData') || dmlNode.data()
  const dmlChainNode = {
    id: startNodeId,
    name: `${dmlData?.operationType || 'DML'} (${dmlData?.className || ''}.${dmlData?.methodName || ''})`,
    type: 'DMLOperation',
    node: dmlNode
  }
  
  buildChain(startNodeId, [dmlChainNode])
  
  return chains
}

// 高亮显示单条调用链路
const highlightSingleCallChain = (dmlNode, chain) => {
  if (!cy) return
  
  // 重置所有元素样式
  cy.elements().removeClass('highlighted caller-path chain-node')
  
  // 重置所有边的样式
  cy.edges().style({
    'line-color': '',
    'target-arrow-color': '',
    'source-arrow-color': '',
    'width': ''
  })
  
  const chainNodes = new Set()
  const chainEdges = new Set()
  const relatedEdges = new Set()
  
  // 收集链路中的节点和边
  chain.forEach((chainNode, nodeIndex) => {
    chainNodes.add(chainNode.id)
    
    // 添加连接到下一个节点的边
    if (nodeIndex < chain.length - 1) {
      const nextNode = chain[nodeIndex + 1]
      const edge = cy.edges().filter(edge => {
        return edge.source().id() === nextNode.id && edge.target().id() === chainNode.id
      })
      if (edge.length > 0) {
        chainEdges.add(edge.id())
      }
    }
  })
  
  // 收集链路节点之间的所有关系边（不仅仅是调用链路）
  chainNodes.forEach(nodeId => {
    const node = cy.getElementById(nodeId)
    
    // 找到该节点的所有相关边
    const connectedEdges = node.connectedEdges()
    connectedEdges.forEach(edge => {
      const sourceId = edge.source().id()
      const targetId = edge.target().id()
      
      // 如果边的两端都在链路节点中，则保留这条边
      if (chainNodes.has(sourceId) && chainNodes.has(targetId)) {
        relatedEdges.add(edge.id())
      }
    })
  })
  
  // 合并链路边和相关边
  const allRelevantEdges = new Set([...chainEdges, ...relatedEdges])
  
  // 隐藏所有不在链路中的节点
  cy.nodes().forEach(node => {
    if (!chainNodes.has(node.id())) {
      node.style('display', 'none')
    } else {
      node.style('display', 'element')
    }
  })
  
  // 隐藏不相关的边，但保留链路节点之间的所有关系
  cy.edges().forEach(edge => {
    if (!allRelevantEdges.has(edge.id())) {
      edge.style('display', 'none')
    } else {
      edge.style('display', 'element')
    }
  })
  
  // 高亮链路中的节点
  chainNodes.forEach(nodeId => {
    const node = cy.getElementById(nodeId)
    if (nodeId === dmlNode.id()) {
      node.addClass('highlighted') // DML节点用红色高亮
    } else {
      node.addClass('caller-path') // 调用者节点用橙色高亮
    }
  })
  
  // 高亮调用链路中的边并设置样式
  chainEdges.forEach(edgeId => {
    const edge = cy.getElementById(edgeId)
    edge.addClass('highlighted caller-path')
    // 动态设置边的样式
    edge.style({
      'line-color': '#ffa502',
      'target-arrow-color': '#ffa502',
      'source-arrow-color': '#ffa502',
      'width': 5
    })
  })
  
  // 对链路中的节点进行聚焦
  const chainCyNodes = cy.nodes().filter(node => chainNodes.has(node.id()))
  cy.fit(chainCyNodes, 80) // 聚焦到链路节点，留80px边距
  
  // 设置链路查看模式
  hasChainView.value = true
  
  // 显示恢复按钮提示
  ElMessage({
    message: '正在显示调用链路，链路节点间的所有关系都已保留。点击"恢复完整视图"可返回全图',
    type: 'info',
    duration: 4000
  })
  
  // 15秒后自动恢复显示所有节点
  setTimeout(() => {
    if (hasChainView.value) {
      restoreFullGraph()
    }
  }, 15000) // 延长到15秒，给用户更多时间查看
}

// 恢复完整图形显示
const restoreFullGraph = () => {
  if (!cy) return
  
  // 恢复所有节点和边的显示
  cy.elements().style('display', 'element')
  
  // 移除所有高亮样式
  cy.elements().removeClass('highlighted caller-path chain-node')
  
  // 重置边的样式
  cy.edges().style({
    'line-color': '',
    'target-arrow-color': '',
    'source-arrow-color': '',
    'width': ''
  })
  
  // 恢复全图视图
  cy.fit(null, 50)
  
  // 清除链路查看模式
  hasChainView.value = false
  
  ElMessage({
    message: '已恢复完整图形视图',
    type: 'success',
    duration: 2000
  })
}

// 高亮显示所有调用链路
const highlightAllCallChains = (dmlNode, callChains) => {
  if (!cy) return
  
  // 重置所有元素样式
  cy.elements().removeClass('highlighted caller-path chain-node')
  
  const allNodes = new Set()
  const allEdges = new Set()
  const allRelatedEdges = new Set()
  
  // 收集所有链路中的节点和边
  callChains.forEach((chain, chainIndex) => {
    chain.forEach((chainNode, nodeIndex) => {
      allNodes.add(chainNode.id)
      
      // 添加连接到下一个节点的边
      if (nodeIndex < chain.length - 1) {
        const nextNode = chain[nodeIndex + 1]
        const edge = cy.edges().filter(edge => {
          return edge.source().id() === nextNode.id && edge.target().id() === chainNode.id
        })
        if (edge.length > 0) {
          allEdges.add(edge.id())
        }
      }
    })
  })
  
  // 收集所有链路节点之间的关系边
  allNodes.forEach(nodeId => {
    const node = cy.getElementById(nodeId)
    
    // 找到该节点的所有相关边
    const connectedEdges = node.connectedEdges()
    connectedEdges.forEach(edge => {
      const sourceId = edge.source().id()
      const targetId = edge.target().id()
      
      // 如果边的两端都在链路节点中，则保留这条边
      if (allNodes.has(sourceId) && allNodes.has(targetId)) {
        allRelatedEdges.add(edge.id())
      }
    })
  })
  
  // 合并调用链路边和相关边
  const allRelevantEdges = new Set([...allEdges, ...allRelatedEdges])
  
  // 隐藏所有不在链路中的节点
  cy.nodes().forEach(node => {
    if (!allNodes.has(node.id())) {
      node.style('display', 'none')
    } else {
      node.style('display', 'element')
    }
  })
  
  // 隐藏不相关的边，但保留链路节点之间的所有关系
  cy.edges().forEach(edge => {
    if (!allRelevantEdges.has(edge.id())) {
      edge.style('display', 'none')
    } else {
      edge.style('display', 'element')
    }
  })
  
  // 高亮所有相关节点
  allNodes.forEach(nodeId => {
    const node = cy.getElementById(nodeId)
    if (nodeId === dmlNode.id()) {
      node.addClass('highlighted') // DML节点用红色高亮
    } else {
      node.addClass('caller-path') // 调用者节点用橙色高亮
    }
  })
  
  // 高亮所有相关边并设置样式
  allEdges.forEach(edgeId => {
    const edge = cy.getElementById(edgeId)
    edge.addClass('highlighted caller-path')
    // 动态设置边的样式
    edge.style({
      'line-color': '#ffa502',
      'target-arrow-color': '#ffa502',
      'source-arrow-color': '#ffa502',
      'width': 4
    })
  })
  
  // 设置链路查看模式
  hasChainView.value = true
  
  // 聚焦到所有链路节点
  const allCyNodes = cy.nodes().filter(node => allNodes.has(node.id()))
  cy.fit(allCyNodes, 60)
  
  // 显示恢复按钮提示
  ElMessage({
    message: '正在显示所有调用链路，链路节点间的所有关系都已保留。点击"恢复完整视图"可返回全图',
    type: 'info',
    duration: 4000
  })
  
  // 15秒后自动恢复显示所有节点
  setTimeout(() => {
    if (hasChainView.value) {
      restoreFullGraph()
    }
  }, 15000)
}

// 适应视图
const fitView = () => {
  if (cy) {
    cy.fit(null, 50)
  }
}

// 节点类型过滤
const toggleNodeType = (type) => {
  if (activeNodeTypes.value.has(type)) {
    activeNodeTypes.value.delete(type)
  } else {
    activeNodeTypes.value.add(type)
  }
  filterGraph()
}

const clearFilter = () => {
  activeNodeTypes.value.clear()
  filterGraph()
}

const filterGraph = () => {
  if (!cy) return
  
  if (activeNodeTypes.value.size === 0) {
    // 显示所有节点
    cy.elements().removeClass('filtered')
  } else {
    // 过滤节点
    cy.nodes().forEach(node => {
      const nodeType = node.data('type')
      if (activeNodeTypes.value.has(nodeType)) {
        node.removeClass('filtered')
      } else {
        node.addClass('filtered')
      }
    })
    
    // 过滤边：只显示两端节点都可见的边
    cy.edges().forEach(edge => {
      const source = edge.source()
      const target = edge.target()
      if (source.hasClass('filtered') || target.hasClass('filtered')) {
        edge.addClass('filtered')
      } else {
        edge.removeClass('filtered')
      }
    })
  }
}

// 生命周期
onMounted(() => {
  loadGraph(false) // 初次加载不显示成功消息
})

onUnmounted(() => {
  if (cy) {
    cy.destroy()
  }
})
</script>

<style scoped>
.graph-view {
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f7fa;
  overflow: hidden;
}

.toolbar {
  padding: 16px;
  background: transparent;
  display: flex;
  gap: 12px;
  flex-shrink: 0;
  align-items: center;
  flex-wrap: wrap;
}

.graph-container {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.cy-container {
  width: 100%;
  height: 100%;
  background: #fafafa;
}

.legend {
  position: absolute;
  bottom: 20px;
  right: 20px;
  background: white;
  padding: 16px;
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  min-width: 200px;
  z-index: 10;
}

.legend h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #303133;
}

.legend-item {
  display: flex;
  align-items: center;
  padding: 8px;
  margin: 4px 0;
  cursor: pointer;
  border-radius: 4px;
  transition: all 0.3s;
}

.legend-item:hover {
  background: #f5f7fa;
}

.legend-item.active {
  background: #ecf5ff;
  border-left: 3px solid #409eff;
}

.legend-item.inactive {
  opacity: 0.4;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  margin-right: 8px;
}

.count {
  margin-left: auto;
  color: #909399;
  font-size: 12px;
}

.node-detail {
  height: calc(100vh - 100px);
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0;
}

.detail-descriptions {
  width: 100%;
}

.detail-value {
  word-wrap: break-word;
  word-break: break-all;
  white-space: pre-wrap;
  max-width: 100%;
  overflow-x: auto;
  overflow-y: auto;
  max-height: 300px;
  padding: 4px;
  line-height: 1.6;
}

/* 自定义滚动条样式 */
.node-detail::-webkit-scrollbar,
.detail-value::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.node-detail::-webkit-scrollbar-track,
.detail-value::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.node-detail::-webkit-scrollbar-thumb,
.detail-value::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
}

.node-detail::-webkit-scrollbar-thumb:hover,
.detail-value::-webkit-scrollbar-thumb:hover {
  background: #555;
}

/* Element Plus Descriptions 单元格样式调整 */
:deep(.el-descriptions__body) {
  background-color: #fff;
}

:deep(.el-descriptions__label) {
  width: 120px;
  min-width: 120px;
  max-width: 120px;
  word-wrap: break-word;
  vertical-align: top;
}

:deep(.el-descriptions__content) {
  word-wrap: break-word;
  word-break: break-all;
  overflow-wrap: break-word;
}

:deep(.el-descriptions-item__cell) {
  padding: 12px 16px;
}

/* 源代码查看器样式 */
.source-code-section {
  margin-top: 20px;
}

.code-viewer {
  background-color: #f5f5f5;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  overflow: auto;
  max-height: 600px;
}

.code-viewer pre {
  margin: 0;
  padding: 16px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.5;
}

.code-viewer code {
  color: #333;
  background-color: transparent;
}

/* 移除节点详情中 descriptions 的边框 */
:deep(.node-detail-drawer .el-descriptions) {
  border: none !important;
}

/* 节点详情抽屉 header 高度统一为 60px */
:deep(.node-detail-drawer.el-drawer .el-drawer__header) {
  height: 60px;
  margin-bottom: 0;
  padding: 0 20px;
  display: flex;
  align-items: center;
  border-bottom: 2px solid #333 !important;
  border-top: none !important;
  border-right: none !important;
}

:deep(.node-detail-drawer.el-drawer .el-drawer__title) {
  font-size: 18px;
  font-weight: bold;
}

:deep(.node-detail-drawer.el-drawer .el-drawer__body) {
  padding: 20px;
  border-top: none !important;
}

/* 移除 drawer 的上下右边框,只保留左边框 */
:deep(.node-detail-drawer.el-drawer) {
  border-top: none !important;
  border-bottom: none !important;
  border-right: none !important;
  border-left: 2px solid var(--wireframe-border) !important;
  box-shadow: -2px 0 8px rgba(0, 0, 0, 0.15) !important;
}
</style>

<style>
/* 非 scoped 全局样式 - 最高优先级覆盖 wireframe.css */
.node-detail-drawer.el-drawer {
  border-top: none !important;
  border-bottom: none !important;
  border-right: none !important;
  border-left: 2px solid var(--wireframe-border) !important;
}

.node-detail-drawer.el-drawer .el-drawer__header {
  border-top: none !important;
  border-right: none !important;
}

/* 右键菜单的节点高亮边框改为白色 */
.cy-cxtmenu-spotlight {
  stroke: white !important;
  stroke-width: 3px !important;
  fill: none !important;
}

/* 针对 SVG circle 元素 */
#cy-cxtmenu-spotlight circle,
.cy-cxtmenu-spotlight circle {
  stroke: white !important;
  stroke-width: 3px !important;
  fill: none !important;
}

/* DML调用者对话框样式 */
.dml-callers-dialog .el-message-box__message {
  white-space: pre-line;
  font-family: 'Consolas', 'Monaco', 'Menlo', monospace;
  font-size: 14px;
  line-height: 1.5;
}

.dml-callers-dialog .el-message-box {
  max-width: 600px;
}
</style>

<style>
/* Cytoscape图形样式 - 需要全局作用域 */
.highlighted {
  border-width: 4px !important;
  border-color: #ff4757 !important;
  border-style: solid !important;
}

.caller-path {
  border-color: #ffa502 !important;
  background-color: #ffa502 !important;
  opacity: 0.9 !important;
}

.chain-node {
  border-color: #2ed573 !important;
  background-color: #2ed573 !important;
  opacity: 0.8 !important;
}
</style>
