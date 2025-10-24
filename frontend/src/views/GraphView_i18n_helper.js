// GraphView.vue 国际化替换映射
// 使用此文件作为参考,手动或脚本化替换

export const replacements = [
  // Header
  { search: 'AST 图可视化', replace: "{{ $t('graph.title') }}" },
  { search: '>刷新<', replace: ">{{ $t('common.refresh') }}<" },
  { search: '>适应窗口<', replace: ">{{ $t('graph.fitView') }}<" },
  
  // Legend
  { search: '图例(点击过滤)', replace: "{{ $t('graph.legend') }}" },
  { search: '>Apex类<', replace: ">{{ $t('graph.apexClass') }}<" },
  { search: '>方法<', replace: ">{{ $t('graph.method') }}<" },
  { search: '>SOQL查询<', replace: ">{{ $t('graph.soqlQuery') }}<" },
  { search: '>DML操作<', replace: ">{{ $t('graph.dmlOperation') }}<" },
  { search: '>清除过滤<', replace: ">{{ $t('graph.clearFilter') }}<" },
  
  // Context Menu
  { search: '展示当前链路所有节点', replace: "{{ $t('graph.contextMenu.showPath') }}" },
  { search: '聚焦此节点', replace: "{{ $t('graph.contextMenu.focus') }}" },
  { search: '查看详细信息', replace: "{{ $t('graph.contextMenu.details') }}" },
  
  // Drawer
  { search: 'title="节点详情"', replace: ":title=\"$t('graph.nodeDetails')\"" },
  { search: 'label="类型"', replace: ":label=\"$t('graph.type')\"" },
  { search: 'label="类名"', replace: ":label=\"$t('graph.className')\"" },
  { search: 'label="简单名称"', replace: ":label=\"$t('graph.simpleName')\"" },
  { search: 'label="访问修饰符"', replace: ":label=\"$t('graph.accessModifier')\"" },
  { search: 'label="共享设置"', replace: ":label=\"$t('graph.sharingSettings')\"" },
  { search: 'label="文件名"', replace: ":label=\"$t('graph.fileName')\"" },
  { search: 'label="方法名"', replace: ":label=\"$t('graph.methodName')\"" },
  { search: 'label="所属类"', replace: ":label=\"$t('graph.belongsToClass')\"" },
  { search: 'label="返回类型"', replace: ":label=\"$t('graph.returnType')\"" },
  { search: 'label="参数数量"', replace: ":label=\"$t('graph.paramCount')\"" },
  { search: 'label="修饰符"', replace: ":label=\"$t('graph.modifiers')\"" },
  { search: 'label="规范名称"', replace: ":label=\"$t('graph.canonicalName')\"" },
  { search: 'label="所属方法"', replace: ":label=\"$t('graph.belongsToMethod')\"" },
  { search: 'label="查询语句"', replace: ":label=\"$t('graph.queryStatement')\"" },
  { search: 'label="规范查询"', replace: ":label=\"$t('graph.canonicalQuery')\"" },
  { search: 'label="操作类型"', replace: ":label=\"$t('graph.operationType')\"" },
  { search: 'label="类型标识"', replace: ":label=\"$t('graph.typeIdentifier')\"" },
  
  // Tags
  { search: '>公开<', replace: ">{{ $t('graph.public') }}<" },
  { search: '>私有<', replace: ">{{ $t('graph.private') }}<" },
  { search: '>public<', replace: ">{{ $t('graph.public') }}<" },
  { search: '>static<', replace: ">{{ $t('graph.static') }}<" },
  { search: '>constructor<', replace: ">{{ $t('graph.constructor') }}<" },
  
  // Path Dialog
  { search: '节点链路分析', replace: "{{ $t('graph.pathAnalysis.title') }}" },
  { search: '直接连接', replace: "{{ $t('graph.pathAnalysis.directConnections') }}" },
  { search: '完整路径', replace: "{{ $t('graph.pathAnalysis.allPaths') }}" },
  { search: '统计', replace: "{{ $t('graph.pathAnalysis.statistics') }}" },
  { search: '目标节点', replace: "{{ $t('graph.pathAnalysis.targetNode') }}" },
  { search: '关系', replace: "{{ $t('graph.pathAnalysis.relationship') }}" },
  { search: '属性', replace: "{{ $t('graph.pathAnalysis.properties') }}" },
  { search: '没有直接连接的节点', replace: "{{ $t('graph.pathAnalysis.noDirectConnections') }}" },
  { search: '没有找到连接路径', replace: "{{ $t('graph.pathAnalysis.noPaths') }}" },
  { search: '路径', replace: "{{ $t('graph.pathAnalysis.path') }}" },
  { search: '深度', replace: "{{ $t('graph.pathAnalysis.depth') }}" },
  { search: '直接连接数', replace: "{{ $t('graph.pathAnalysis.directConnectionCount') }}" },
  { search: '所有路径数', replace: "{{ $t('graph.pathAnalysis.allPathCount') }}" },
  { search: '最长路径深度', replace: "{{ $t('graph.pathAnalysis.maxPathDepth') }}" },
  { search: '涉及节点数', replace: "{{ $t('graph.pathAnalysis.uniqueNodeCount') }}" },
  
  // Messages (JS)
  { search: "'图数据加载成功'", replace: "t('graph.loadSuccess')" },
  { search: "'加载图数据失败'", replace: "t('graph.loadError')" },
  { search: "'请先选择一个节点'", replace: "t('graph.selectNodeFirst') }}" },
]

// Script部分需要添加:
/*
<script setup>
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
// ... 其他代码
</script>
*/
