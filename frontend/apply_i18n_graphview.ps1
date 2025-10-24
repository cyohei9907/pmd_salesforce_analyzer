# GraphView.vue 国际化自动替换脚本
# 使用方法: .\apply_i18n_graphview.ps1

$filePath = ".\src\views\GraphView.vue"
$backupPath = ".\src\views\GraphView.vue.backup"

# 创建备份
Copy-Item $filePath $backupPath -Force
Write-Host "已创建备份: $backupPath" -ForegroundColor Green

# 读取文件内容
$content = Get-Content $filePath -Raw -Encoding UTF8

# 定义替换规则
$replacements = @(
    # Header - 精确替换
    @{ Old = '<span>AST 图可视化</span>'; New = '<span>{{ $t(''graph.title'') }}</span>' }
    @{ Old = '<el-button @click="loadGraph" :icon="Refresh" :loading="loading">刷新</el-button>'; New = '<el-button @click="loadGraph" :icon="Refresh" :loading="loading">{{ $t(''common.refresh'') }}</el-button>' }
    @{ Old = '<el-button @click="fitView" :icon="FullScreen">适应窗口</el-button>'; New = '<el-button @click="fitView" :icon="FullScreen">{{ $t(''graph.fitView'') }}</el-button>' }
    
    # Legend
    @{ Old = '<h4>图例（点击过滤）</h4>'; New = '<h4>{{ $t(''graph.legend'') }}</h4>' }
    @{ Old = '<span>Apex类</span>'; New = '<span>{{ $t(''graph.apexClass'') }}</span>' }
    @{ Old = '<span>方法</span>'; New = '<span>{{ $t(''graph.method'') }}</span>' }
    @{ Old = '<span>SOQL查询</span>'; New = '<span>{{ $t(''graph.soqlQuery'') }}</span>' }
    @{ Old = '<span>DML操作</span>'; New = '<span>{{ $t(''graph.dmlOperation'') }}</span>' }
    @{ Old = '            清除过滤'; New = '            {{ $t(''graph.clearFilter'') }}' }
    
    # Context Menu
    @{ Old = '<span>展示当前链路所有节点</span>'; New = '<span>{{ $t(''graph.contextMenu.showPath'') }}</span>' }
    @{ Old = '<span>聚焦此节点</span>'; New = '<span>{{ $t(''graph.contextMenu.focus'') }}</span>' }
    @{ Old = '<span>查看详细信息</span>'; New = '<span>{{ $t(''graph.contextMenu.details'') }}</span>' }
    
    # Drawer title
    @{ Old = 'title="节点详情"'; New = ':title="$t(''graph.nodeDetails'')"' }
    
    # Labels - 使用动态绑定
    @{ Old = 'label="类型"'; New = ':label="$t(''graph.type'')"' }
    @{ Old = 'label="类名"'; New = ':label="$t(''graph.className'')"' }
    @{ Old = 'label="简单名称"'; New = ':label="$t(''graph.simpleName'')"' }
    @{ Old = 'label="访问修饰符"'; New = ':label="$t(''graph.accessModifier'')"' }
    @{ Old = 'label="共享设置"'; New = ':label="$t(''graph.sharingSettings'')"' }
    @{ Old = 'label="文件名"'; New = ':label="$t(''graph.fileName'')"' }
    @{ Old = 'label="方法名"'; New = ':label="$t(''graph.methodName'')"' }
    @{ Old = 'label="所属类"'; New = ':label="$t(''graph.belongsToClass'')"' }
    @{ Old = 'label="返回类型"'; New = ':label="$t(''graph.returnType'')"' }
    @{ Old = 'label="参数数量"'; New = ':label="$t(''graph.paramCount'')"' }
    @{ Old = 'label="修饰符"'; New = ':label="$t(''graph.modifiers'')"' }
    @{ Old = 'label="规范名称"'; New = ':label="$t(''graph.canonicalName'')"' }
    @{ Old = 'label="所属方法"'; New = ':label="$t(''graph.belongsToMethod'')"' }
    @{ Old = 'label="查询语句"'; New = ':label="$t(''graph.queryStatement'')"' }
    @{ Old = 'label="规范查询"'; New = ':label="$t(''graph.canonicalQuery'')"' }
    @{ Old = 'label="操作类型"'; New = ':label="$t(''graph.operationType'')"' }
    @{ Old = 'label="类型标识"'; New = ':label="$t(''graph.typeIdentifier'')"' }
    
    # Tag texts
    @{ Old = '<el-tag type="primary">Apex类</el-tag>'; New = '<el-tag type="primary">{{ $t(''graph.apexClass'') }}</el-tag>' }
    @{ Old = '<el-tag type="success">方法</el-tag>'; New = '<el-tag type="success">{{ $t(''graph.method'') }}</el-tag>' }
    @{ Old = '<el-tag type="warning">SOQL查询</el-tag>'; New = '<el-tag type="warning">{{ $t(''graph.soqlQuery'') }}</el-tag>' }
    @{ Old = '<el-tag type="danger">DML操作</el-tag>'; New = '<el-tag type="danger">{{ $t(''graph.dmlOperation'') }}</el-tag>' }
    
    # Path dialog
    @{ Old = 'title="节点链路分析"'; New = ':title="$t(''graph.pathAnalysis.title'')"' }
    @{ Old = 'description="没有直接连接的节点"'; New = ':description="$t(''graph.pathAnalysis.noDirectConnections'')"' }
    @{ Old = 'description="没有找到连接路径"'; New = ':description="$t(''graph.pathAnalysis.noPaths'')"' }
    
    # JS messages
    @{ Old = "ElMessage.success(`图数据加载成功"; New = "ElMessage.success(`" + '${t(''graph.loadSuccess'')}' }
    @{ Old = "ElMessage.error('加载图数据失败"; New = "ElMessage.error(t('graph.loadError')" }
    @{ Old = "ElMessage.warning('请先选择一个节点')"; New = "ElMessage.warning(t('graph.selectNodeFirst'))" }
    
    # Add import statement after other imports
    @{ Old = "import { ref, onMounted, onBeforeUnmount, computed } from 'vue'"; New = "import { ref, onMounted, onBeforeUnmount, computed } from 'vue'`nimport { useI18n } from 'vue-i18n'" }
    
    # Add const { t } after existing consts
    @{ Old = "let network = null"; New = "let network = null`nconst { t } = useI18n()" }
)

# 执行替换
foreach ($replacement in $replacements) {
    $content = $content.Replace($replacement.Old, $replacement.New)
}

# 保存文件
$content | Set-Content $filePath -Encoding UTF8 -NoNewline

Write-Host "✅ 替换完成!" -ForegroundColor Green
Write-Host "📝 请手动检查文件并测试" -ForegroundColor Yellow
Write-Host "💾 备份文件: $backupPath" -ForegroundColor Cyan
