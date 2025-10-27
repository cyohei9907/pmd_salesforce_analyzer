# 测试多仓库功能

## 前端已实现功能 ✅

1. **RepositorySelector 组件** - 仓库选择器
   - 下拉菜单显示所有仓库
   - 显示活动仓库标记(绿色勾)
   - 显示每个仓库的文件数量
   - "添加仓库"按钮和对话框

2. **GraphView 更新**
   - 工具栏集成了仓库选择器
   - 切换仓库时自动重新加载对应的图数据
   - 支持按仓库过滤图形展示

## 测试步骤

### 1. 启动应用

使用VS Code的launch配置启动前后端:
- 按 `F5`
- 选择 "Full Stack (Frontend + Backend)"

或手动启动:

**后端:**
```powershell
cd backend
D:\workspace\project019_pmdgithub\pmd_salesforce_analyzer\.venv\Scripts\python.exe manage.py runserver
```

**前端:**
```powershell
cd frontend
npm run dev
```

### 2. 访问图形视图

1. 打开浏览器访问: `http://localhost:5173`
2. 点击左侧菜单的 "图形视图"

### 3. 测试仓库选择器

在图形视图的顶部工具栏,你应该能看到:
- **仓库下拉选择器** - 显示当前所有仓库
- **添加仓库按钮** - 用于克隆新仓库

### 4. 添加新仓库

点击"添加仓库"按钮,填写信息:

**测试仓库1 (dreamhouse-lwc):**
```
仓库URL: https://github.com/trailheadapps/dreamhouse-lwc.git
分支: main
Apex目录: force-app/main/default/classes
设为活动仓库: ✓
自动导入: ✓
```

**测试仓库2 (lwc-recipes):**
```
仓库URL: https://github.com/trailheadapps/lwc-recipes.git
分支: main
Apex目录: force-app/main/default/classes
设为活动仓库: ✓
自动导入: ✓
```

点击"添加并克隆"后,系统会:
1. 克隆Git仓库到 `project/<repo_name>/`
2. 使用PMD分析Apex代码
3. 生成AST文件到 `output/ast/<repo_name>/`
4. 自动导入到图数据库
5. 刷新图形显示

### 5. 切换仓库查看

1. 从下拉菜单中选择不同的仓库
2. 图形会自动重新加载,只显示该仓库的代码结构
3. 活动仓库会有绿色勾标记

### 6. 验证数据隔离

**检查目录结构:**
```powershell
# 查看仓库目录
ls project/

# 查看AST文件目录
ls output/ast/

# 应该看到每个仓库都有独立的文件夹
```

**检查数据库:**
```powershell
cd backend
D:\workspace\project019_pmdgithub\pmd_salesforce_analyzer\.venv\Scripts\python.exe manage.py shell
```

```python
from ast_api.models import Repository, ASTFile

# 查看所有仓库
repos = Repository.objects.all()
for repo in repos:
    print(f"{repo.name}: {repo.ast_files.count()} files")

# 查看活动仓库
active = Repository.objects.filter(is_active=True).first()
print(f"Active: {active.name if active else 'None'}")
```

## 预期结果

### 仓库列表
- ✅ 可以看到所有已添加的仓库
- ✅ 每个仓库显示文件数量
- ✅ 活动仓库有绿色勾标记

### 切换仓库
- ✅ 选择不同仓库时,图形自动更新
- ✅ 只显示当前选中仓库的类、方法、SOQL等
- ✅ 节点数量和类型统计正确

### 添加仓库
- ✅ 成功克隆远程仓库
- ✅ 自动分析Apex代码
- ✅ 自动导入图数据
- ✅ 刷新仓库列表

## 功能特点

1. **数据隔离**
   - 每个仓库的文件独立存储
   - 图数据通过repository属性标识
   - 可以完美支持多个项目同时管理

2. **自动化流程**
   - 克隆 → 分析 → 导入一键完成
   - 无需手动干预

3. **智能切换**
   - 切换仓库时自动过滤图数据
   - 保持界面流畅

4. **状态管理**
   - 同时只有一个活动仓库
   - 活动仓库有明显标识

## 故障排查

### 问题1: 看不到仓库选择器
**原因:** 前端可能有编译错误
**解决:** 
```powershell
cd frontend
npm run dev
# 查看终端输出是否有错误
```

### 问题2: 切换仓库后没有数据
**原因:** 该仓库可能没有AST数据
**解决:**
1. 确认仓库已成功克隆
2. 检查 `output/ast/<repo_name>/` 是否有XML文件
3. 手动导入: 访问 "导入数据" 页面

### 问题3: 添加仓库失败
**原因:** Git克隆失败或PMD分析失败
**解决:**
1. 检查网络连接
2. 确认Git仓库URL正确
3. 查看后端日志输出
4. 尝试使用 `--depth 1` 浅克隆

## API端点测试

如果前端有问题,可以直接测试后端API:

```powershell
# 获取仓库列表
curl http://localhost:8000/api/repositories/

# 添加仓库
curl -X POST http://localhost:8000/api/repositories/clone/ `
  -H "Content-Type: application/json" `
  -d '{\"repo_url\":\"https://github.com/trailheadapps/lwc-recipes.git\",\"branch\":\"main\",\"auto_import\":true,\"set_active\":true}'

# 获取仓库图数据
curl http://localhost:8000/api/repositories/1/graph/
```

## 成功标准

- ✅ 可以添加多个Git仓库
- ✅ 可以在仓库间切换查看
- ✅ 每个仓库的数据完全隔离
- ✅ 图形展示正确且流畅
- ✅ 文件数量统计准确

---

**测试日期:** 2025-10-27
**版本:** v1.0.0 多仓库功能
