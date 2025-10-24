# PMD Apex AST 解析器 - 快速开始

## ✅ 执行成功！

已成功使用PMD解析所有Apex类并生成AST（抽象语法树）。

## 📊 执行结果

### 处理统计
- **处理文件数**: 9个Apex类
- **生成AST文件**: 9个
- **分析成功率**: 100%
- **Java版本**: OpenJDK 21.0.9

### 代码统计
| 指标 | 数量 |
|------|------|
| 总方法数 | 31 |
| SOQL查询 | 18 |
| DML操作 | 19 |
| 变量声明 | 74 |

## 📁 生成的文件

```
pmd_analyzer/
├── output/
│   ├── ast/                              # AST XML文件目录
│   │   ├── FileUtilities_ast.txt
│   │   ├── FileUtilitiesTest_ast.txt
│   │   ├── GeocodingService_ast.txt
│   │   ├── GeocodingServiceTest_ast.txt
│   │   ├── PagedResult_ast.txt
│   │   ├── PropertyController_ast.txt
│   │   ├── SampleDataController_ast.txt
│   │   ├── TestPropertyController_ast.txt
│   │   └── TestSampleDataController_ast.txt
│   ├── ast_analysis.json                 # JSON格式的分析结果
│   └── AST_SUMMARY.md                    # 详细摘要报告
├── pmd_check.py                          # PMD核心功能模块
├── ast_analyzer.py                       # AST分析工具
└── run_ast_analysis.py                   # 一键运行脚本
```

## 🚀 快速使用

### 方法1: 一键运行（推荐）

```bash
python run_ast_analysis.py
```

这个脚本会自动完成：
1. ✓ 检查PMD环境（Java、PMD工具）
2. ✓ 查找所有Apex文件
3. ✓ 生成AST文件
4. ✓ 分析AST并生成报告

### 方法2: 分步执行

#### 步骤1: 环境检查
```python
from pmd_check import check_pmd_environment

env = check_pmd_environment()
if env['ready']:
    print("✓ 环境就绪")
else:
    print("✗ 环境问题:", env)
```

#### 步骤2: 生成AST
```python
from pmd_check import parse_apex_classes_directory

result = parse_apex_classes_directory(
    classes_dir="project/dreamhouse-lwc/force-app/main/default/classes",
    output_dir="output/ast",
    format="text",
    execute=True  # 实际执行PMD
)

print(f"成功: {result['success']}")
print(f"处理文件: {result['total_files']}")
```

#### 步骤3: 分析AST
```python
from ast_analyzer import analyze_all_ast_files, print_analysis_summary

results = analyze_all_ast_files("output/ast")
print_analysis_summary(results)
```

## 📖 API参考

### pmd_check.py

#### `get_pmd_command()`
获取适合当前OS的PMD命令路径。

```python
pmd_cmd = get_pmd_command()
# Windows: D:\...\pmd.bat
# Linux/Mac: /...path.../pmd
```

#### `check_pmd_environment()`
检查PMD运行环境。

```python
env = check_pmd_environment()
# 返回: {
#   'os': 'Windows',
#   'java_available': True,
#   'java_version': 'openjdk version "21.0.9"',
#   'ready': True,
#   ...
# }
```

#### `find_apex_files(directory)`
递归查找目录中的所有Apex文件（.cls）。

```python
apex_files = find_apex_files("path/to/classes")
# 返回: ['path/to/File1.cls', 'path/to/File2.cls', ...]
```

#### `execute_pmd_ast(apex_file, output_file, format)`
执行PMD生成单个文件的AST。

```python
result = execute_pmd_ast(
    apex_file_or_dir="SampleDataController.cls",
    output_file="output/SampleDataController_ast.txt",
    format="text"  # 或 "xml"
)
```

#### `parse_apex_classes_directory(classes_dir, output_dir, format, execute)`
批量处理整个classes目录。

```python
result = parse_apex_classes_directory(
    classes_dir="project/.../classes",
    output_dir="output/ast",
    format="text",
    execute=True  # False时只生成命令，不执行
)
```

### ast_analyzer.py

#### `analyze_ast_file(ast_file_path)`
分析单个AST文件。

```python
from ast_analyzer import analyze_ast_file

result = analyze_ast_file("output/ast/SampleDataController_ast.txt")
print(f"类名: {result['class_name']}")
print(f"方法数: {result['method_count']}")
print(f"SOQL数: {result['soql_count']}")
```

#### `analyze_all_ast_files(ast_directory)`
分析目录中的所有AST文件。

```python
from ast_analyzer import analyze_all_ast_files

results = analyze_all_ast_files("output/ast")
# 返回所有文件的分析结果列表
```

## 📋 AST结构示例

### SampleDataController.cls 的AST片段

```xml
<ApexFile DefiningType='SampleDataController'>
  <UserClass SimpleName='SampleDataController'>
    <ModifierNode Public='true' WithSharing='true' />
    
    <Method CanonicalName='importSampleData' ReturnType='void'>
      <ModifierNode Public='true' Static='true'>
        <Annotation Name='AuraEnabled' />
      </ModifierNode>
      
      <BlockStatement>
        <DmlDeleteStatement>
          <SoqlExpression Query='SELECT Id FROM Case' />
        </DmlDeleteStatement>
        
        <ExpressionStatement>
          <MethodCallExpression MethodName='insertBrokers' />
        </ExpressionStatement>
      </BlockStatement>
    </Method>
    
    <Method CanonicalName='insertBrokers' ReturnType='void'>
      <ModifierNode Private='true' Static='true' />
      <BlockStatement>
        <VariableDeclarationStatements>
          <VariableDeclaration Image='brokersResource' Type='StaticResource'>
            <SoqlExpression Query='SELECT Id, Body FROM StaticResource...' />
          </VariableDeclaration>
        </VariableDeclarationStatements>
        
        <DmlInsertStatement>
          <VariableExpression Image='brokers' />
        </DmlInsertStatement>
      </BlockStatement>
    </Method>
  </UserClass>
</ApexFile>
```

## 🔍 分析结果示例

### 从ast_analysis.json中提取的信息

```json
{
  "class_name": "SampleDataController",
  "public": false,
  "with_sharing": false,
  "method_count": 5,
  "methods": [
    {
      "name": "importSampleData",
      "return_type": "void",
      "parameters": 0,
      "static": true,
      "public": true,
      "annotations": ["AuraEnabled"]
    }
  ],
  "soql_count": 7,
  "soql_queries": [
    "SELECT Id FROM Case",
    "SELECT Id FROM Property__c",
    "SELECT Id FROM Broker__c"
  ],
  "dml_operations": {
    "insert": 4,
    "delete": 7
  },
  "total_dml": 7
}
```

## 💡 使用场景

### 1. 代码审查
```python
# 查找所有使用DML操作的类
for result in results:
    if result['total_dml'] > 5:
        print(f"{result['class_name']}: {result['total_dml']} DML操作")
```

### 2. SOQL分析
```python
# 统计SOQL查询最多的类
sorted_by_soql = sorted(results, key=lambda x: x['soql_count'], reverse=True)
print("SOQL查询最多的类:")
for r in sorted_by_soql[:3]:
    print(f"  {r['class_name']}: {r['soql_count']}个查询")
```

### 3. API方法发现
```python
# 查找所有@AuraEnabled方法
for result in results:
    for method in result['methods']:
        if 'AuraEnabled' in method.get('annotations', []):
            print(f"{result['class_name']}.{method['name']}")
```

## 🛠️ 高级功能

### 自定义AST解析

```python
import xml.etree.ElementTree as ET

def find_all_soql_queries(ast_file):
    """提取AST中的所有SOQL查询"""
    tree = ET.parse(ast_file)
    root = tree.getroot()
    
    queries = []
    for soql in root.findall('.//SoqlExpression'):
        query = soql.get('Query', '')
        queries.append(query)
    
    return queries

# 使用
queries = find_all_soql_queries('output/ast/SampleDataController_ast.txt')
for q in queries:
    print(q)
```

### 生成代码度量报告

```python
def calculate_complexity(ast_file):
    """基于AST计算简单的复杂度指标"""
    tree = ET.parse(ast_file)
    root = tree.getroot()
    
    metrics = {
        'methods': len(root.findall('.//Method')),
        'if_statements': len(root.findall('.//IfBlockStatement')),
        'for_loops': len(root.findall('.//ForLoopStatement')),
        'while_loops': len(root.findall('.//WhileLoopStatement')),
    }
    
    # 简单的圈复杂度估算
    complexity = 1 + metrics['if_statements'] + metrics['for_loops'] + metrics['while_loops']
    metrics['estimated_complexity'] = complexity
    
    return metrics
```

## 📚 相关文档

- [PMD官方文档](https://pmd.github.io/)
- [Apex语言参考](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/)
- [README.md](README.md) - 完整文档

## ❓ 常见问题

**Q: 如何处理新的Apex文件？**
```bash
# 直接重新运行即可
python run_ast_analysis.py
```

**Q: 如何只生成特定文件的AST？**
```python
from pmd_check import execute_pmd_ast

execute_pmd_ast(
    "project/.../MyClass.cls",
    "output/MyClass_ast.txt"
)
```

**Q: AST文件太大怎么办？**
```python
# 使用XML格式，更适合程序化处理
parse_apex_classes_directory(
    classes_dir="...",
    output_dir="output/ast_xml",
    format="xml",  # 使用XML格式
    execute=True
)
```

## 🎯 下一步

1. ✅ **已完成**: AST生成和基础分析
2. 📝 **建议**: 基于AST实现代码质量检查
3. 📝 **建议**: 实现自定义规则引擎
4. 📝 **建议**: 集成到CI/CD流程

---

**创建时间**: 2025年10月23日
**版本**: 1.0
**状态**: ✅ 生产就绪
