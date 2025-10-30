# 自动检测Salesforce项目结构功能

## 功能概述

系统现在可以在克隆Git仓库后,自动检测Salesforce项目结构,包括:
- **Apex类** (.cls文件)
- **LWC组件** (Lightning Web Components)
- **Visualforce页面** (.page文件)

## 实现细节

### 后端实现

#### 1. 新增检测方法 (git_service.py)

```python
def detect_salesforce_structure(repo_name):
    """自动检测Salesforce项目结构"""
    # 返回:
    # - apex_classes: Apex类路径和数量
    # - lwc_components: LWC组件路径和数量  
    # - visualforce_pages: Visualforce页面路径和数量
```

**检测的常见路径:**
- Apex: `force-app/main/default/classes`, `src/classes`, `classes`
- LWC: `force-app/main/default/lwc`, `src/lwc`, `lwc`
- Visualforce: `force-app/main/default/pages`, `src/pages`, `pages`

#### 2. 更新API端点

**新增端点:**
```
POST /api/git/detect-structure/
{
  "repo_name": "dreamhouse-lwc"
}
```

**更新clone-and-analyze端点:**
克隆后自动调用检测,并使用检测到的Apex路径进行分析

### 前端实现

#### 1. 导入数据页面更新

**显示检测结果:**
```vue
<el-alert v-if="detectedStructure" type="success">
  <div v-if="detectedStructure.apex_classes">
    Apex类: force-app/main/default/classes (10个文件)
  </div>
  <div v-if="detectedStructure.lwc_components">
    LWC组件: force-app/main/default/lwc (15个组件)
  </div>
  <div v-if="detectedStructure.visualforce_pages">
    Visualforce页面: force-app/main/default/pages (5个文件)
  </div>
</el-alert>
```

**Apex路径自动填充:**
- 检测到Apex类后,自动设置路径
- 输入框变为禁用状态(显示"已自动检测")
- 移除"重置"按钮(不再需要)

## 使用流程

### 完整的代码分析流程

1. **克隆仓库** (步骤1)
   - 从Git远程仓库克隆代码到本地
   - 保存到 `project/<repo_name>/`

2. **检测项目结构** (步骤2)
   - 自动扫描项目目录
   - 识别Apex类、LWC组件、Visualforce页面的位置

3. **显示检测结果** (步骤3)
   - 在前端显示检测到的资源
   - 自动填充Apex代码路径

4. **AST解析** (步骤4) - 核心分析步骤
   - **使用PMD生成AST**: 对每个Apex类文件(.cls)运行PMD的`ast-dump`命令
   - **生成XML**: PMD将源代码解析为抽象语法树(AST),输出为XML格式
   - **保存AST文件**: XML保存到 `output/ast/<repo_name>/<ClassName>_ast.xml`
   - **解析AST**: 使用`ast_parser.py`解析XML,提取:
     - 类信息(名称、修饰符、共享模式)
     - 方法信息(签名、参数、返回类型)
     - SOQL查询(SELECT语句)
     - DML操作(INSERT、UPDATE、DELETE等)
     - 方法调用关系

5. **导入图数据库** (步骤5)
   - 将解析后的AST数据转换为图结构
   - 创建节点(类、方法、SOQL、DML)
   - 创建关系(HAS_METHOD、CONTAINS_SOQL等)
   - 存储到Neo4j或本地图数据库

### 1. 导入数据页面

1. 点击 "从Git仓库导入" 标签
2. 输入Git仓库URL
3. 点击 "克隆并分析"
4. 系统自动:
   - 克隆仓库
   - 检测项目结构
   - 显示检测结果(绿色提示框)
   - 使用检测到的路径分析Apex代码
   - 导入到图数据库

### 2. 仓库选择器

在图形视图的仓库选择器中添加新仓库时,同样支持自动检测。

## 检测结果示例

### dreamhouse-lwc 项目

```json
{
  "success": true,
  "repo_name": "dreamhouse-lwc",
  "apex_classes": {
    "path": "force-app/main/default/classes",
    "count": 9
  },
  "lwc_components": {
    "path": "force-app/main/default/lwc",
    "count": 20
  },
  "visualforce_pages": null,
  "detected_paths": [
    "Apex类: force-app/main/default/classes (9个文件)",
    "LWC组件: force-app/main/default/lwc (20个组件)"
  ]
}
```

### lwc-recipes 项目

```json
{
  "success": true,
  "repo_name": "lwc-recipes",
  "apex_classes": {
    "path": "force-app/main/default/classes",
    "count": 20
  },
  "lwc_components": {
    "path": "force-app/main/default/lwc",
    "count": 80
  },
  "visualforce_pages": null,
  "detected_paths": [
    "Apex类: force-app/main/default/classes (20个文件)",
    "LWC组件: force-app/main/default/lwc (80个组件)"
  ]
}
```

## 优势

1. **自动化**: 无需手动输入Apex路径
2. **准确性**: 自动检测实际项目结构
3. **可视化**: 清晰显示检测到的资源数量
4. **灵活性**: 支持多种Salesforce项目结构

## 界面变化

### 之前
```
Apex代码路径: [____________________] [重置]
提示: 相对于仓库根目录的Apex类文件路径
```

### 之后(检测到结构时)
```
✅ 已自动检测项目结构
  Apex类: force-app/main/default/classes (9个文件)
  LWC组件: force-app/main/default/lwc (20个组件)

Apex代码路径: [force-app/main/default/classes] (禁用)
提示: 已自动检测
```

## 兼容性

- ✅ 支持标准SFDX项目结构
- ✅ 支持旧版Metadata API项目结构
- ✅ 自动fallback到默认路径(如果检测失败)
- ✅ 向后兼容旧的导入方式

## 测试

### 测试仓库

1. **dreamhouse-lwc**
   ```
   URL: https://github.com/trailheadapps/dreamhouse-lwc.git
   预期: 检测到Apex和LWC
   ```

2. **lwc-recipes**
   ```
   URL: https://github.com/trailheadapps/lwc-recipes.git
   预期: 检测到Apex和LWC
   ```

### 验证步骤

1. 导入仓库
2. 检查是否显示绿色检测结果框
3. 确认Apex路径自动填充
4. 验证文件数量是否正确
5. 确认分析成功

## API测试

```bash
# 克隆并自动检测
curl -X POST http://localhost:8000/api/git/clone-and-analyze/ \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/trailheadapps/dreamhouse-lwc.git",
    "branch": "main",
    "auto_import": true
  }'

# 单独检测项目结构
curl -X POST http://localhost:8000/api/git/detect-structure/ \
  -H "Content-Type: application/json" \
  -d '{"repo_name": "dreamhouse-lwc"}'
```

## 未来增强

- [ ] 支持检测Aura组件
- [ ] 支持检测自定义对象
- [ ] 支持检测触发器(Triggers)
- [ ] 导出项目结构报告
- [ ] 可视化项目结构树

---

**更新日期**: 2025-10-27
**版本**: v1.1.0
