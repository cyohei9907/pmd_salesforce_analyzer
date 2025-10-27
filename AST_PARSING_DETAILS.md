# AST解析流程详解

## 概述

本系统使用PMD(Programming Mistake Detector)对Salesforce Apex代码进行抽象语法树(AST)解析,然后将解析结果导入图数据库进行可视化分析。

## 完整流程

### 1. Git仓库克隆
```
输入: Git仓库URL
工具: git clone --depth 1
输出: project/<repo_name>/
```

### 2. 项目结构检测
```python
# git_service.detect_salesforce_structure()
检测路径:
- Apex类: force-app/main/default/classes/*.cls
- LWC组件: force-app/main/default/lwc/*/
- Visualforce: force-app/main/default/pages/*.page
```

### 3. PMD AST生成 (核心步骤)

#### 3.1 执行PMD命令
```bash
pmd ast-dump \
  --language apex \
  --format xml \
  --file /path/to/PropertyController.cls
```

#### 3.2 PMD处理流程
```
Apex源代码 (.cls)
    ↓
[PMD词法分析器]
    ↓
Token流
    ↓
[PMD语法分析器]
    ↓
抽象语法树 (AST)
    ↓
[XML序列化器]
    ↓
AST XML文件
```

#### 3.3 生成的AST XML结构
```xml
<?xml version="1.0" encoding="UTF-8"?>
<CompilationUnit>
  <UserClass SimpleName="PropertyController" DefiningType="PropertyController">
    <ModifierNode Public="true" WithSharing="true"/>
    
    <Method MethodName="getPagedPropertyList" ReturnType="PagedResult" Arity="2">
      <Parameter Name="searchKey" Type="String"/>
      <Parameter Name="pageSize" Type="Integer"/>
      
      <BlockStatement>
        <!-- SOQL查询 -->
        <SoqlExpression Query="SELECT Id, Name FROM Property__c WHERE Name LIKE :searchKey"/>
        
        <!-- DML操作 -->
        <DmlInsertStatement/>
        
        <!-- 方法调用 -->
        <MethodCallExpression MethodName="doSomething" FullMethodName="HelperClass.doSomething"/>
      </BlockStatement>
    </Method>
  </UserClass>
</CompilationUnit>
```

### 4. AST XML解析

#### 4.1 Python解析器 (ast_parser.py)
```python
class ASTParser:
    def parse(self):
        # 1. 加载XML
        tree = ET.parse(ast_file)
        root = tree.getroot()
        
        # 2. 提取类信息
        class_info = self._extract_class_info()
        # - 类名
        # - 访问修饰符 (public/private)
        # - 共享模式 (with sharing/without sharing)
        
        # 3. 提取方法信息
        methods = self._extract_methods()
        # - 方法签名
        # - 参数列表
        # - 返回类型
        
        # 4. 提取SOQL查询
        soql_queries = self._extract_soql_queries()
        # - 查询语句
        # - 规范化查询
        
        # 5. 提取DML操作
        dml_operations = self._extract_dml_operations()
        # - INSERT, UPDATE, DELETE等
        
        # 6. 提取方法调用
        method_calls = self._extract_method_calls()
        # - 调用的方法名
        # - 完整方法路径
```

#### 4.2 提取的数据结构
```python
{
    'name': 'PropertyController',
    'simpleName': 'PropertyController',
    'definingType': 'PropertyController',
    'public': True,
    'withSharing': True,
    'fileName': 'PropertyController.cls',
    'methods': [
        {
            'name': 'getPagedPropertyList',
            'returnType': 'PagedResult',
            'arity': 2,
            'public': True,
            'static': False,
            'constructor': False,
            'parameters': [
                {'name': 'searchKey', 'type': 'String'},
                {'name': 'pageSize', 'type': 'Integer'}
            ],
            'soql_queries': [
                {
                    'query': 'SELECT Id, Name FROM Property__c WHERE Name LIKE :searchKey',
                    'canonicalQuery': 'SELECT Id, Name FROM Property__c WHERE Name LIKE :?'
                }
            ],
            'dml_operations': [
                {'type': 'INSERT', 'tag': 'DmlInsertStatement'}
            ],
            'method_calls': [
                {
                    'methodName': 'doSomething',
                    'fullMethodName': 'HelperClass.doSomething'
                }
            ]
        }
    ]
}
```

### 5. 图数据库导入 (import_service.py)

#### 5.1 创建图节点
```python
# 类节点
CREATE (c:ApexClass {
    name: 'PropertyController',
    public: true,
    withSharing: true,
    repository: 'dreamhouse-lwc'
})

# 方法节点
CREATE (m:ApexMethod {
    canonicalName: 'PropertyController.getPagedPropertyList',
    name: 'getPagedPropertyList',
    returnType: 'PagedResult',
    arity: 2
})

# SOQL节点
CREATE (s:SOQLQuery {
    query: 'SELECT Id, Name FROM Property__c...',
    canonicalQuery: 'SELECT Id, Name FROM Property__c...'
})

# DML节点
CREATE (d:DMLOperation {
    type: 'INSERT',
    operation: 'DmlInsertStatement'
})
```

#### 5.2 创建图关系
```python
# 类包含方法
CREATE (c)-[:HAS_METHOD]->(m)

# 方法包含SOQL
CREATE (m)-[:CONTAINS_SOQL {query: '...'}]->(s)

# 方法包含DML
CREATE (m)-[:CONTAINS_DML {type: 'INSERT'}]->(d)

# 方法调用方法
CREATE (m1)-[:CALLS {methodName: 'doSomething'}]->(m2)
```

#### 5.3 图结构示例
```
PropertyController (ApexClass)
    │
    ├─[HAS_METHOD]─> getPagedPropertyList (ApexMethod)
    │                   │
    │                   ├─[CONTAINS_SOQL]─> SELECT Id, Name... (SOQLQuery)
    │                   │
    │                   ├─[CONTAINS_DML]─> INSERT (DMLOperation)
    │                   │
    │                   └─[CALLS]─> HelperClass.doSomething (ApexMethod)
    │
    └─[HAS_METHOD]─> saveProperty (ApexMethod)
```

## 技术栈

### PMD (Programming Mistake Detector)
- **版本**: 7.17.0
- **语言支持**: Apex, Java, JavaScript等
- **功能**: 
  - 静态代码分析
  - AST生成
  - 代码质量检查

### AST (Abstract Syntax Tree)
- **定义**: 源代码的树状抽象表示
- **优势**:
  - 保留代码结构信息
  - 方便程序化分析
  - 支持深度代码理解

### 图数据库
- **Neo4j**: 可选的图数据库(如果启用)
- **本地图**: 基于NetworkX的轻量级实现
- **优势**:
  - 自然表示代码关系
  - 支持复杂查询
  - 可视化展示

## 关键文件

### 后端
```
backend/ast_api/
├── git_service.py          # Git操作和PMD调用
├── ast_parser.py           # AST XML解析
├── import_service.py       # 图数据库导入
├── unified_graph_service.py # 图服务统一接口
└── views.py                # REST API端点
```

### 生成的文件
```
output/ast/<repo_name>/
├── PropertyController_ast.xml
├── SampleDataController_ast.xml
└── ...

graphdata/
├── entities.json           # 图节点数据
└── relations.json          # 图关系数据
```

## 性能考虑

### PMD AST生成
- **单文件耗时**: 约1-3秒
- **并行处理**: 串行处理(避免资源竞争)
- **超时设置**: 60秒/文件

### AST XML解析
- **单文件耗时**: 约0.1-0.5秒
- **内存占用**: 取决于AST复杂度
- **优化**: 使用ElementTree增量解析

### 图数据导入
- **本地图**: 快速,适合中小型项目
- **Neo4j**: 适合大型项目,支持复杂查询
- **批量处理**: 一次导入多个AST文件

## 示例:完整处理流程

### 输入
```bash
POST /api/git/clone-and-analyze/
{
  "repo_url": "https://github.com/trailheadapps/dreamhouse-lwc.git",
  "branch": "main",
  "auto_import": true
}
```

### 处理步骤
1. Git克隆到 `project/dreamhouse-lwc/`
2. 检测到9个Apex类文件
3. 对每个文件执行:
   ```
   PropertyController.cls
   → pmd ast-dump
   → PropertyController_ast.xml
   → AST解析
   → 提取:3个方法, 5个SOQL, 2个DML
   → 导入图数据库
   ```
4. 创建图结构:
   - 9个ApexClass节点
   - 27个ApexMethod节点
   - 45个SOQLQuery节点
   - 18个DMLOperation节点
   - 100+个关系

### 输出
```json
{
  "success": true,
  "structure": {
    "apex_classes": {"path": "force-app/main/default/classes", "count": 9}
  },
  "analyze": {
    "total_files": 9,
    "analyzed": 9,
    "failed": 0
  },
  "import": {
    "total": 9,
    "successful": 9,
    "failed": 0
  }
}
```

## 可视化结果

在图形视图中可以:
- 查看类之间的依赖关系
- 追踪方法调用链
- 分析SOQL查询分布
- 识别DML操作热点
- 发现潜在的代码问题

## 扩展可能

### 未来可以解析的内容
- [ ] Trigger (触发器)
- [ ] Aura组件
- [ ] Visualforce页面
- [ ] 自定义对象定义
- [ ] 权限和配置文件
- [ ] 测试覆盖率

### 增强分析
- [ ] 循环依赖检测
- [ ] 代码复杂度计算
- [ ] 安全漏洞分析
- [ ] 性能优化建议

---

**技术文档**
**版本**: v1.0.0
**更新日期**: 2025-10-27
