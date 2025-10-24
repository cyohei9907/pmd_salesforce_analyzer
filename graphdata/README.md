# GraphData 目录

此目录用于存储本地图数据库的数据。

## 目录结构

```
graphdata/
├── entities/           # 实体文件（节点数据）
│   ├── ApexClass_*.json
│   ├── ApexMethod_*.json
│   └── ...
│
├── relations/          # 关系文件（边数据）
│   ├── *__HAS_METHOD__*.json
│   ├── *__CONTAINS_SOQL__*.json
│   └── ...
│
├── graphs/             # 图数据库文件
│   └── main_graph.gpickle    # NetworkX 图对象
│
└── exports/            # 导出文件
    ├── graph_export_*.json    # JSON 格式导出
    └── graph_export_*.gexf    # GEXF 格式导出（可用于 Gephi）
```

## 文件说明

### Entities（实体文件）

每个实体对应一个 JSON 文件，包含节点的所有属性：

```json
{
  "node_id": "class:PropertyController",
  "attributes": {
    "type": "ApexClass",
    "name": "PropertyController",
    "simpleName": "PropertyController",
    "public": true,
    "withSharing": true,
    "fileName": "PropertyController.cls",
    "created_at": "2025-10-24T21:00:00.000000"
  }
}
```

### Relations（关系文件）

每个关系对应一个 JSON 文件，包含边的所有属性：

```json
{
  "from_node": "class:PropertyController",
  "to_node": "method:PropertyController.getPagedPropertyList",
  "type": "HAS_METHOD",
  "properties": {
    "description": "Class contains method",
    "created_at": "2025-10-24T21:00:00.000000"
  }
}
```

### Graphs（图数据库）

- `main_graph.gpickle`: NetworkX 图对象的序列化文件
  - 包含完整的图结构（节点和边）
  - 使用 Python pickle 格式存储
  - 自动加载和保存

### Exports（导出文件）

- `graph_export_*.json`: JSON 格式的图导出
  - 可读性好
  - 易于分享和导入其他系统
  
- `graph_export_*.gexf`: GEXF 格式的图导出
  - 可用于 Gephi、Cytoscape 等图分析工具
  - 支持节点和边的属性

## 使用方式

### 自动创建

当系统启动时，`LocalGraphService` 会自动创建此目录结构。

### 导入 AST 数据

导入 AST 数据时，系统会自动：
1. 创建实体文件到 `entities/`
2. 创建关系文件到 `relations/`
3. 更新 `graphs/main_graph.gpickle`

### 导出图数据

```python
from backend.ast_api.unified_graph_service import unified_graph_service

# 导出为 JSON
unified_graph_service.export_local_graph(format='json')

# 导出为 GEXF（用于 Gephi）
unified_graph_service.export_local_graph(format='gexf')
```

## 数据持久化

- 所有图数据自动保存到 `graphs/main_graph.gpickle`
- 每次创建节点或边时，同时保存到对应的 JSON 文件
- 系统重启后自动加载已存在的图数据

## 性能说明

- **本地存储**: 无需数据库服务器，轻量级
- **快速访问**: 内存中操作，性能优秀
- **适合场景**: 小到中型项目（<10000 节点）
- **推荐升级**: 大型项目建议使用 Neo4j

## 与 Neo4j 的对比

| 特性 | 本地图数据库 | Neo4j |
|------|-------------|-------|
| **安装** | 无需安装 | 需要安装服务 |
| **性能** | 中等 | 高 |
| **规模** | < 10K 节点 | > 百万节点 |
| **查询语言** | Python API | Cypher |
| **可视化** | 支持（JSON/GEXF） | 原生支持 |
| **适用场景** | 开发/测试 | 生产环境 |

## 备份和恢复

### 备份
```bash
# 备份整个 graphdata 目录
cp -r graphdata/ graphdata_backup_$(date +%Y%m%d)/
```

### 恢复
```bash
# 恢复备份
cp -r graphdata_backup_20251024/ graphdata/
```

### 清空数据
```python
from backend.ast_api.unified_graph_service import unified_graph_service

# 清空所有图数据
unified_graph_service.clear_database()
```

## 注意事项

1. **文件权限**: 确保应用有读写权限
2. **磁盘空间**: 根据项目规模预留足够空间
3. **并发访问**: 本地图数据库不支持多进程并发写入
4. **数据迁移**: 可通过导出/导入功能迁移到 Neo4j

## 常见问题

### Q: graphdata 目录在哪里？
A: 默认在项目根目录下。可以通过环境变量配置：
```python
GRAPH_DATA_DIR=./graphdata
```

### Q: 如何查看图数据？
A: 三种方式：
1. 通过 API 接口查询
2. 导出为 JSON 查看
3. 导出为 GEXF 用 Gephi 可视化

### Q: 数据丢失了怎么办？
A: 
1. 检查 `graphs/main_graph.gpickle` 是否存在
2. 查看 `entities/` 和 `relations/` 下的 JSON 文件
3. 从备份恢复
4. 重新导入 AST 文件

### Q: 如何升级到 Neo4j？
A:
1. 导出本地图数据为 JSON
2. 启动 Neo4j 服务
3. 配置 Neo4j 连接
4. 重新导入 AST 文件（会自动同时写入 Neo4j 和本地）

## 开发说明

相关代码文件：
- `backend/ast_api/local_graph_service.py` - 本地图数据库服务
- `backend/ast_api/unified_graph_service.py` - 统一图服务接口
- `backend/ast_api/import_service.py` - AST 导入服务

## 许可证

此目录下的数据文件遵循项目主许可证。
