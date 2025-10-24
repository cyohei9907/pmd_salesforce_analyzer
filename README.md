# PMD Salesforce Analyzer

基于 PMD 的 Salesforce Apex 代码分析工具，提供 AST（抽象语法树）解析和图数据库可视化功能。

## 📋 目录

- [系统架构](#系统架构)
- [快速启动](#快速启动)
- [核心原理](#核心原理)
- [主要功能](#主要功能)
- [方法流程](#方法流程)
- [使用示例](#使用示例)
- [故障排查](#故障排查)

---

## 🏗️ 系统架构

### 整体架构

```
┌─────────────────────────────────────────────────────────────┐
│                    PMD Salesforce Analyzer                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐      ┌──────────────┐                     │
│  │  Apex 源码    │ ---> │  PMD 解析器   │ ---> AST 输出      │
│  └──────────────┘      └──────────────┘                     │
│                              │                                │
│                              v                                │
│                    ┌──────────────────┐                      │
│                    │  AST 解析服务     │                      │
│                    └──────────────────┘                      │
│                              │                                │
│                    ┌─────────┴──────────┐                    │
│                    v                     v                    │
│          ┌──────────────┐      ┌──────────────┐             │
│          │  Neo4j 数据库 │      │  本地图数据库 │             │
│          │   (可选)      │      │  (NetworkX)  │             │
│          └──────────────┘      └──────────────┘             │
│                    │                     │                    │
│                    └─────────┬───────────┘                    │
│                              v                                │
│                    ┌──────────────────┐                      │
│                    │  统一图服务接口   │                      │
│                    └──────────────────┘                      │
│                              │                                │
│                              v                                │
│                    ┌──────────────────┐                      │
│                    │   REST API 服务  │                      │
│                    └──────────────────┘                      │
│                              │                                │
│                              v                                │
│                    ┌──────────────────┐                      │
│                    │  Vue.js 前端界面 │                      │
│                    └──────────────────┘                      │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 技术栈

**后端**:
- Python 3.8+
- Django 4.2.7 (REST API)
- NetworkX 3.2.1 (本地图数据库)
- Neo4j 5.14+ (可选的云图数据库)
- PMD 7.17.0 (AST 解析)
- Java 8+ (PMD 运行时)

**前端**:
- Vue 3.3.4
- Vite 5.0.0
- Vue Router 4.2.4
- Axios (HTTP 客户端)

---

## 🚀 快速启动

### 方式一: 一键安装 + 启动 (推荐)

**Windows**:
```batch
# 1. 安装环境
setup_environment.bat

# 2. 启动服务（交互式菜单）
quick_start.bat
```

**Linux/Mac**:
```bash
# 1. 安装环境
chmod +x setup_environment.sh
./setup_environment.sh

# 2. 启动服务（交互式菜单）
chmod +x quick_start.sh
./quick_start.sh
```

### 方式二: 手动启动

#### 1. 环境检查
```bash
python environment_check.py
```

#### 2. 启动后端服务
```bash
cd backend
python manage.py runserver
```

#### 3. 启动前端服务
```bash
cd frontend
npm run dev
```

#### 4. 访问应用
- 前端界面: http://localhost:5173
- 后端API: http://localhost:8000/api/

---

## 🔍 核心原理

### 1. AST 解析原理

```
Apex 源码 (.cls) 
    ↓
PMD 解析器 (Java)
    ↓
抽象语法树 (AST)
    ↓
AST 解析服务 (Python)
    ↓
图节点和关系
```

**PMD 解析流程**:
1. 读取 Apex 源代码文件
2. 使用 PMD 的 Apex 语言模块进行词法和语法分析
3. 生成 AST（包含类、方法、字段、调用关系等）
4. 输出为 Text 或 XML 格式

**AST 数据提取**:
- **类节点**: `UserClass` → 类名、修饰符、继承关系
- **方法节点**: `Method` → 方法名、参数、返回类型
- **字段节点**: `Field` → 字段名、类型、修饰符
- **SOQL查询**: `SoqlExpression` → SQL查询语句
- **调用关系**: `MethodCall` → 方法调用链

### 2. 图数据库原理

#### 双后端架构

系统支持两种图数据库后端，可自动切换：

**Neo4j 模式** (推荐用于生产):
- 高性能图数据库
- 支持百万级节点
- Cypher 查询语言
- 原生可视化界面

**本地模式** (适合开发测试):
- 基于 NetworkX 的内存图
- 无需安装数据库服务
- 数据持久化到本地文件
- 轻量级，适合小型项目

#### 自动降级机制

```python
# 统一图服务自动选择可用后端
if Neo4j 可用:
    if NetworkX 可用:
        模式 = "双后端" (数据同时写入两者)
    else:
        模式 = "Neo4j 单后端"
else:
    if NetworkX 可用:
        模式 = "本地单后端"
    else:
        错误: "无可用图数据库"
```

### 3. 数据存储结构

#### Neo4j 存储
```cypher
// 节点
(:ApexClass {name, public, withSharing, ...})
(:ApexMethod {name, static, public, ...})

// 关系
(class)-[:HAS_METHOD]->(method)
(method)-[:CALLS]->(method)
(class)-[:CONTAINS_SOQL]->(query)
```

#### 本地存储 (graphdata/)
```
graphdata/
├── entities/              # 节点数据 (JSON)
│   ├── ApexClass_PropertyController_20251024210000.json
│   └── ApexMethod_getPagedPropertyList_20251024210001.json
├── relations/             # 关系数据 (JSON)
│   └── PropertyController__HAS_METHOD__getPagedPropertyList.json
├── graphs/                # 图对象 (pickle)
│   └── main_graph.gpickle
└── exports/               # 导出文件
    ├── graph_export_20251024.json
    └── graph_export_20251024.gexf (Gephi格式)
```

---

## 🎯 主要功能

### 1. 环境检查

**功能**: 自动检测系统环境是否满足运行要求

**检查项目**:
- ✅ Java 环境 (必需)
- ✅ Neo4j 连接 (可选)
- ✅ NetworkX 库 (必需)
- ✅ PMD 工具
- ✅ Python/Node.js 版本

**使用方法**:
```bash
# 完整环境检查
python environment_check.py

# 快速检查
python check_environment.py

# PMD专项检查
python pmd_check.py
```

### 2. AST 解析

**功能**: 将 Apex 代码解析为抽象语法树

**支持格式**:
- Text 格式 (树形结构，易读)
- XML 格式 (结构化，易解析)

**批量处理**: 自动扫描目录，批量解析所有 .cls 文件

### 3. 图数据导入

**功能**: 将 AST 数据转换为图节点和关系

**导入流程**:
1. 解析 AST 文件
2. 提取类、方法、字段信息
3. 创建图节点
4. 创建关系 (HAS_METHOD, CALLS, CONTAINS_SOQL 等)
5. 持久化到图数据库

### 4. 图数据可视化

**功能**: 通过 Web 界面可视化代码结构

**可视化类型**:
- 类图 (显示所有类及其关系)
- 方法调用图 (显示方法调用链)
- 依赖关系图 (显示模块依赖)

### 5. 数据导出

**功能**: 导出图数据到外部格式

**支持格式**:
- JSON (通用数据交换格式)
- GEXF (Gephi 可视化工具格式)

---

## 📊 方法流程

### 流程 1: AST 解析流程

```python
# 主要方法

def parse_apex_classes_directory(classes_dir, output_dir, format, execute):
    """批量解析 Apex 类目录"""
    
    # 1. 查找所有 .cls 文件
    apex_files = find_apex_files(classes_dir)
    
    # 2. 为每个文件生成 AST
    for apex_file in apex_files:
        output_file = generate_output_path(apex_file, output_dir)
        
        if execute:
            # 3. 执行 PMD 解析
            execute_pmd_ast(apex_file, output_file, format)
    
    return result
```

**详细步骤**:

1. **查找 Apex 文件** (`find_apex_files`)
   ```python
   # 递归扫描目录
   for root, dirs, files in os.walk(classes_dir):
       for file in files:
           if file.endswith('.cls'):
               apex_files.append(os.path.join(root, file))
   ```

2. **构建 PMD 命令** (`parse_apex_ast`)
   ```python
   # 获取 PMD 命令路径
   pmd_cmd = get_pmd_command()  # pmd.bat 或 pmd
   
   # 构建命令
   command = [
       pmd_cmd,
       'ast-dump',
       '--language', 'apex',
       '--format', format,  # text 或 xml
       '--file', apex_file
   ]
   ```

3. **执行 PMD** (`execute_pmd_ast`)
   ```python
   # 执行命令
   result = subprocess.run(
       command,
       stdout=subprocess.PIPE,
       stderr=subprocess.PIPE,
       text=True,
       encoding='utf-8'
   )
   
   # 保存输出
   if output_file:
       with open(output_file, 'w', encoding='utf-8') as f:
           f.write(result.stdout)
   ```

### 流程 2: 图数据导入流程

```python
# 主要方法
def import_ast_to_graph(file_path, content):
    """导入 AST 到图数据库"""
    
    # 1. 解析 AST 内容
    ast_data = parse_ast_content(content)
    
    # 2. 提取类信息
    class_info = extract_class_info(ast_data)
    
    # 3. 创建类节点
    unified_graph_service.create_class_node(class_info)
    
    # 4. 提取方法信息
    methods = extract_methods(ast_data)
    
    # 5. 创建方法节点和关系
    for method in methods:
        unified_graph_service.create_method_node(method)
        unified_graph_service.create_relationship(
            class_info['name'],
            method['name'],
            'HAS_METHOD'
        )
    
    # 6. 提取 SOQL 查询
    soql_queries = extract_soql_queries(ast_data)
    
    # 7. 创建 SOQL 关系
    for query in soql_queries:
        unified_graph_service.create_relationship(
            method['name'],
            query,
            'CONTAINS_SOQL'
        )
    
    return result
```

**详细步骤**:

1. **AST 解析** (`parse_ast_content`)
   ```python
   # 解析 AST 文本/XML
   tree = parse_ast_tree(content)
   
   # 提取节点
   nodes = extract_nodes(tree)
   ```

2. **创建图节点** (`create_class_node`, `create_method_node`)
   ```python
   # Neo4j 模式
   session.run("""
       CREATE (c:ApexClass {
           name: $name,
           public: $public,
           withSharing: $withSharing
       })
   """, parameters)
   
   # 本地模式
   local_graph.add_node(node_id, **attributes)
   
   # 同时保存 JSON 文件
   save_entity_json(node_id, attributes)
   ```

3. **创建关系** (`create_relationship`)
   ```python
   # Neo4j 模式
   session.run("""
       MATCH (a {name: $from}), (b {name: $to})
       CREATE (a)-[:HAS_METHOD]->(b)
   """)
   
   # 本地模式
   local_graph.add_edge(from_node, to_node, type='HAS_METHOD')
   
   # 同时保存 JSON 文件
   save_relation_json(from_node, to_node, 'HAS_METHOD')
   ```

### 流程 3: 数据查询流程

```python
# 主要方法
def get_graph_data():
    """获取图数据"""
    
    # 1. 检测后端类型
    backend = unified_graph_service.backend_type
    
    # 2. 根据后端查询
    if 'neo4j' in backend:
        # Neo4j 查询
        result = neo4j_service.get_all_nodes_and_relationships()
    
    if 'local' in backend:
        # 本地查询
        nodes = local_graph_service.get_all_nodes()
        edges = local_graph_service.get_all_edges()
    
    # 3. 格式化返回
    return format_graph_data(nodes, edges)
```

### 流程 4: 数据导出流程

```python
# 主要方法
def export_graph(format='json'):
    """导出图数据"""
    
    # 1. 获取所有节点和边
    nodes = local_graph_service.get_all_nodes()
    edges = local_graph_service.get_all_edges()
    
    # 2. 根据格式导出
    if format == 'json':
        # JSON 格式
        data = {
            'nodes': nodes,
            'edges': edges
        }
        file_path = 'graphdata/exports/graph_export.json'
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    elif format == 'gexf':
        # GEXF 格式 (Gephi)
        import networkx as nx
        nx.write_gexf(graph, 'graphdata/exports/graph_export.gexf')
    
    return file_path
```

---

## 💡 使用示例

### 示例 1: 环境检查

```bash
# 完整环境检查
python environment_check.py
```

输出示例:
```
============================================================
环境检查工具
============================================================

操作系统: Windows 10
Python版本: 3.8.10

------------------------------------------------------------
1. 检查Java环境
------------------------------------------------------------
✅ Java环境可用
   版本: java version "11.0.12"
   JAVA_HOME: C:\Program Files\Java\jdk-11.0.12

------------------------------------------------------------
2. 检查Neo4j数据库连接（可选）
------------------------------------------------------------
连接URI: bolt://localhost:7687
⚠️  Neo4j数据库连接失败（将使用本地图数据库）
   错误: 无法连接到Neo4j数据库

------------------------------------------------------------
3. 检查NetworkX（本地图数据库）
------------------------------------------------------------
✅ NetworkX可用
   版本: 3.2.1

============================================================
环境检查总结
============================================================
✅ 所有必需环境检查通过，系统可以正常运行
   - 图数据库: 本地存储（适合开发和测试）
============================================================
```

### 示例 2: 解析单个 Apex 文件

```python
from pmd_check import execute_pmd_ast

# 解析单个文件
result = execute_pmd_ast(
    apex_file_or_dir="project/dreamhouse-lwc/force-app/main/default/classes/PropertyController.cls",
    output_file="output/ast/PropertyController_ast.txt",
    format="text"
)

if result["success"]:
    print(f"✅ AST解析成功: {result['output_file']}")
else:
    print(f"❌ 解析失败: {result['error']}")
```

### 示例 3: 批量解析 Apex 文件

```python
from pmd_check import parse_apex_classes_directory

# 批量解析整个目录
result = parse_apex_classes_directory(
    classes_dir="project/dreamhouse-lwc/force-app/main/default/classes",
    output_dir="output/ast",
    format="text",
    execute=True
)

print(f"处理文件数: {result['total_files']}")
print(f"成功: {len(result['processed_files'])}")
print(f"失败: {len(result['errors'])}")

# 显示错误
for error in result['errors']:
    print(f"  - {error['file']}: {error['error']}")
```

### 示例 4: 通过 API 导入 AST 到图数据库

```bash
# Windows PowerShell
$file = "output/ast/PropertyController_ast.txt"
$content = Get-Content $file -Raw
$json = @{file_path=$file; content=$content} | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/api/import-ast/ -Method Post -Body $json -ContentType "application/json"

# Linux/Mac Bash
curl -X POST http://localhost:8000/api/import-ast/ \
  -H "Content-Type: application/json" \
  -d "{\"file_path\": \"output/ast/PropertyController_ast.txt\", \"content\": \"$(cat output/ast/PropertyController_ast.txt)\"}"
```

### 示例 5: 查询图数据

```bash
# 获取所有图数据
curl http://localhost:8000/api/graph-data/

# 获取特定类的图数据
curl http://localhost:8000/api/class-graph/PropertyController/

# 获取统计信息
curl http://localhost:8000/api/statistics/
```

返回示例:
```json
{
  "total_classes": 9,
  "total_methods": 27,
  "total_relationships": 36,
  "backend": "local"
}
```

### 示例 6: 导出图数据

```bash
# 导出为 JSON
curl -X POST http://localhost:8000/api/export-graph/ \
  -H "Content-Type: application/json" \
  -d '{"format": "json"}'

# 导出为 GEXF (用于 Gephi)
curl -X POST http://localhost:8000/api/export-graph/ \
  -H "Content-Type: application/json" \
  -d '{"format": "gexf"}'
```

### 示例 7: 在 Gephi 中可视化

1. 导出 GEXF 文件（参考示例 6）
2. 打开 Gephi: https://gephi.org/
3. File → Open → 选择导出的 .gexf 文件
4. 选择布局: Layout → Force Atlas 2 → Run
5. 应用样式: Appearance → Nodes → Color → Partition → type

---

## 🔧 故障排查

### 问题 1: Java 环境未找到

**错误信息**:
```
❌ Java环境不可用
   错误: 未找到Java命令
```

**解决方案**:
```bash
# 1. 检查 Java 是否已安装
java -version

# 2. 如果未安装，下载并安装 Java
# Windows/Mac: https://www.oracle.com/java/technologies/downloads/
# 或 OpenJDK: https://adoptium.net/

# 3. 设置 JAVA_HOME 环境变量
# Windows: 系统属性 → 环境变量 → 新建 JAVA_HOME
# Linux/Mac: export JAVA_HOME=/path/to/jdk
```

### 问题 2: NetworkX 未安装

**错误信息**:
```
❌ NetworkX不可用
   错误: 未安装networkx Python包
```

**解决方案**:
```bash
# 安装 NetworkX
pip install networkx==3.2.1

# 或重新运行环境安装脚本
setup_environment.bat  # Windows
./setup_environment.sh  # Linux/Mac
```

### 问题 3: 端口被占用

**错误信息**:
```
Error: That port is already in use.
```

**解决方案**:
```bash
# Windows - 查找占用端口的进程
netstat -ano | findstr :8000
taskkill /PID <进程ID> /F

# Linux/Mac - 查找并终止进程
lsof -i :8000
kill -9 <进程ID>

# 或使用不同端口启动
python manage.py runserver 8001
```

### 问题 4: graphdata 目录权限错误

**错误信息**:
```
PermissionError: [Errno 13] Permission denied: 'graphdata'
```

**解决方案**:
```bash
# Windows (以管理员运行 PowerShell)
icacls graphdata /grant Users:F /t

# Linux/Mac
chmod -R 755 graphdata/
```

### 问题 5: 前端依赖安装失败

**错误信息**:
```
npm ERR! Failed to install dependencies
```

**解决方案**:
```bash
cd frontend

# 清理 npm 缓存
npm cache clean --force

# 删除 node_modules 和 package-lock.json
rm -rf node_modules package-lock.json  # Linux/Mac
Remove-Item -Recurse -Force node_modules, package-lock.json  # Windows

# 重新安装
npm install
```

---

## 📚 项目结构

```
pmd_salesforce_analyzer/
├── analyzer/                    # PMD 工具
│   ├── bin/
│   │   ├── pmd                 # PMD 命令 (Unix)
│   │   └── pmd.bat             # PMD 命令 (Windows)
│   ├── lib/                    # PMD 库文件
│   └── conf/                   # PMD 配置
│
├── backend/                     # Django 后端
│   ├── manage.py               # Django 管理脚本
│   ├── requirements.txt        # Python 依赖
│   ├── apex_graph/             # Django 项目配置
│   └── ast_api/                # AST API 应用
│       ├── views.py            # API 视图
│       ├── import_service.py   # AST 导入服务
│       ├── neo4j_service.py    # Neo4j 服务
│       ├── local_graph_service.py    # 本地图服务
│       └── unified_graph_service.py  # 统一图服务
│
├── frontend/                    # Vue 前端
│   ├── src/
│   │   ├── App.vue             # 主应用组件
│   │   ├── main.js             # 入口文件
│   │   ├── router/             # 路由配置
│   │   ├── views/              # 视图组件
│   │   │   ├── Home.vue
│   │   │   ├── GraphView.vue   # 图可视化
│   │   │   ├── ImportData.vue  # 数据导入
│   │   │   └── Statistics.vue  # 统计信息
│   │   └── api/                # API 客户端
│   └── package.json            # Node.js 依赖
│
├── graphdata/                   # 本地图数据库存储
│   ├── entities/               # 实体文件 (JSON)
│   ├── relations/              # 关系文件 (JSON)
│   ├── graphs/                 # 图对象 (pickle)
│   └── exports/                # 导出文件 (JSON/GEXF)
│
├── output/                      # AST 输出目录
│   └── ast/                    # AST 文件
│
├── project/                     # Salesforce 项目
│   └── dreamhouse-lwc/         # 示例项目
│
├── pmd_check.py                # PMD 检查和解析
├── environment_check.py        # 环境检查工具
├── setup_environment.bat/sh    # 一键安装脚本
├── quick_start.bat/sh          # 快速启动脚本
└── README.md                   # 本文档
```

---

## 🔐 许可证

本项目使用以下开源软件:

- **PMD**: BSD-style License
- **Django**: BSD License
- **Vue.js**: MIT License
- **NetworkX**: BSD License
- **Neo4j**: Community Edition - GPL v3

---

## 📞 支持

如有问题或建议，请通过以下方式联系:

- 提交 Issue
- 查看项目文档
- 运行环境检查工具排查问题

---

**最后更新**: 2025-10-24
