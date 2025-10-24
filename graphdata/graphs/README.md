# Graphs 图数据库文件

此目录存储 NetworkX 图对象的序列化文件。

## 主要文件

### main_graph.gpickle
- **格式**: Python pickle
- **内容**: 完整的 NetworkX MultiDiGraph 对象
- **自动保存**: 每次修改图时自动保存
- **自动加载**: 服务启动时自动加载

## 使用说明

### 加载图数据
```python
import networkx as nx
import pickle

with open('main_graph.gpickle', 'rb') as f:
    graph = pickle.load(f)

# 查看节点数量
print(f"Nodes: {graph.number_of_nodes()}")

# 查看边数量
print(f"Edges: {graph.number_of_edges()}")
```

### 图分析示例
```python
# 获取所有节点
nodes = list(graph.nodes(data=True))

# 获取所有边
edges = list(graph.edges(data=True))

# 查找特定节点
for node, attrs in graph.nodes(data=True):
    if attrs.get('type') == 'ApexClass':
        print(f"Class: {attrs.get('name')}")

# 查找特定关系
for u, v, data in graph.edges(data=True):
    if data.get('type') == 'HAS_METHOD':
        print(f"{u} -> {v}")
```

## 备份建议

定期备份此文件，避免数据丢失：
```bash
cp main_graph.gpickle main_graph_backup_$(date +%Y%m%d).gpickle
```

## 性能优化

- **内存使用**: 图对象常驻内存，快速访问
- **磁盘空间**: 根据图大小，通常 < 100MB
- **建议**: 超过 10,000 节点建议升级到 Neo4j
