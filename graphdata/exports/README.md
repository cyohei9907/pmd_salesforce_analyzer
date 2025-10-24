# Exports 导出文件

此目录存储图数据的导出文件，支持多种格式。

## 支持的格式

### JSON 格式 (.json)
- **文件名**: `graph_export_{timestamp}.json`
- **用途**: 数据交换、备份、导入其他系统
- **可读性**: 高

示例内容：
```json
{
  "nodes": [
    {
      "id": "class:PropertyController",
      "type": "ApexClass",
      "name": "PropertyController",
      "attributes": {...}
    }
  ],
  "edges": [
    {
      "source": "class:PropertyController",
      "target": "method:PropertyController.getPagedPropertyList",
      "type": "HAS_METHOD",
      "properties": {...}
    }
  ]
}
```

### GEXF 格式 (.gexf)
- **文件名**: `graph_export_{timestamp}.gexf`
- **用途**: 导入 Gephi、Cytoscape 等图分析工具
- **标准**: Graph Exchange XML Format

示例内容：
```xml
<?xml version="1.0" encoding="UTF-8"?>
<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">
  <graph mode="static" defaultedgetype="directed">
    <nodes>
      <node id="class:PropertyController" label="PropertyController">
        <attvalues>
          <attvalue for="type" value="ApexClass"/>
        </attvalues>
      </node>
    </nodes>
    <edges>
      <edge source="class:PropertyController" 
            target="method:PropertyController.getPagedPropertyList" 
            label="HAS_METHOD"/>
    </edges>
  </graph>
</gexf>
```

## 使用方式

### 通过 API 导出
```bash
# 导出为 JSON
curl -X POST http://localhost:8000/api/export-graph/ \
  -H "Content-Type: application/json" \
  -d '{"format": "json"}'

# 导出为 GEXF
curl -X POST http://localhost:8000/api/export-graph/ \
  -H "Content-Type: application/json" \
  -d '{"format": "gexf"}'
```

### 通过 Python 代码导出
```python
from backend.ast_api.unified_graph_service import unified_graph_service

# 导出为 JSON
json_file = unified_graph_service.export_local_graph(format='json')
print(f"Exported to: {json_file}")

# 导出为 GEXF
gexf_file = unified_graph_service.export_local_graph(format='gexf')
print(f"Exported to: {gexf_file}")
```

## 导入 Gephi

1. 打开 Gephi
2. File → Open → 选择 `.gexf` 文件
3. 选择布局算法（如 Force Atlas 2）
4. 运行布局
5. 应用样式和过滤器

## 自动清理

导出文件会保留最近 10 个版本，旧版本自动删除。

## 文件大小估算

- **小型项目** (< 100 类): < 1MB
- **中型项目** (100-500 类): 1-10MB
- **大型项目** (> 500 类): > 10MB
