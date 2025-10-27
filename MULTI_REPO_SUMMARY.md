# 多仓库功能实现总结

## ✅ 已完成的工作

### 1. 数据库模型更新
- ✅ 创建了 `Repository` 模型,支持存储多个Git仓库信息
- ✅ 更新了 `ASTFile` 模型,添加与仓库的关联
- ✅ 添加了数据库迁移文件并执行成功

### 2. 后端API实现
- ✅ **仓库管理API**:
  - `GET/POST /api/repositories/` - 列表和创建
  - `GET/PUT/DELETE /api/repositories/<id>/` - 详情、更新、删除
  - `POST /api/repositories/switch/` - 切换活动仓库
  - `POST /api/repositories/clone/` - 克隆并注册仓库
  - `GET /api/repositories/<id>/graph/` - 获取仓库图数据

- ✅ **序列化器**:
  - `RepositorySerializer` - 仓库数据序列化
  - `ASTFileSerializer` - AST文件数据序列化

### 3. 服务层更新
- ✅ 更新 `git_service.py`:
  - 按仓库分类存储AST文件到 `output/ast/<repo_name>/`
  
- ✅ 更新 `import_service.py`:
  - 支持将AST文件关联到对应的仓库
  - 在图数据中添加仓库属性

- ✅ 更新 `unified_graph_service.py`:
  - 添加 `get_repository_graph()` 方法,按仓库筛选图数据

### 4. 目录结构
```
project/
  ├── dreamhouse-lwc/      # ✅ Git仓库1
  ├── lwc-recipes/         # ✅ Git仓库2(新克隆)
  └── ...

output/ast/
  ├── dreamhouse-lwc/      # ✅ 按仓库分类的AST
  ├── lwc-recipes/
  └── ...

graphdata/
  ├── entities.json        # ✅ 包含repository属性
  └── relations.json
```

## 📝 待实现的工作

### 前端界面
需要在Vue前端添加以下组件:

1. **RepositorySelector组件** (优先级:高)
   - 仓库下拉选择器
   - 添加新仓库的对话框
   - 显示仓库状态和文件数量

2. **更新GraphView** (优先级:高)
   - 集成RepositorySelector
   - 根据选中仓库加载对应的图数据
   - 优化图形展示逻辑

3. **RepositoryManager页面** (优先级:中)
   - 仓库列表展示
   - 仓库详细信息
   - 仓库删除和管理功能

## 🚀 使用方法

### 后端启动
```powershell
cd backend
..\.\venv\Scripts\python.exe manage.py runserver
```

### 测试API (需要后端运行)
```powershell
# 安装requests库(如果需要)
.\.venv\Scripts\pip install requests

# 运行测试脚本
.\.venv\Scripts\python.exe test_multi_repo.py
```

### API使用示例

#### 1. 克隆新仓库
```bash
POST http://localhost:8000/api/repositories/clone/
Content-Type: application/json

{
  "repo_url": "https://github.com/trailheadapps/lwc-recipes.git",
  "branch": "main",
  "apex_dir": "force-app/main/default/classes",
  "auto_import": true,
  "set_active": true
}
```

#### 2. 获取仓库列表
```bash
GET http://localhost:8000/api/repositories/
```

#### 3. 切换仓库
```bash
POST http://localhost:8000/api/repositories/switch/
Content-Type: application/json

{
  "repo_id": 1
}
```

#### 4. 获取仓库图数据
```bash
GET http://localhost:8000/api/repositories/1/graph/
```

## 🎯 核心特性

### 多仓库隔离
- ✅ 每个仓库的代码独立克隆到 `project/<repo_name>/`
- ✅ AST文件分类存储在 `output/ast/<repo_name>/`
- ✅ 图数据中包含 `repository` 和 `repositoryId` 属性
- ✅ 可以按仓库筛选和查看图数据

### 仓库管理
- ✅ 支持添加多个Git仓库
- ✅ 每个仓库独立配置(URL、分支、Apex目录)
- ✅ 可以设置活动仓库
- ✅ 支持删除仓库(同时删除本地文件)

### 自动化流程
- ✅ 克隆 → 分析 → 导入 一键完成
- ✅ 自动创建仓库记录
- ✅ 自动关联AST文件到仓库

## 📊 数据模型

### Repository表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| name | String | 仓库名称(唯一) |
| url | URL | Git仓库URL |
| branch | String | 分支名称 |
| local_path | Text | 本地克隆路径 |
| apex_dir | String | Apex代码目录 |
| is_active | Boolean | 是否为活动仓库 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### ASTFile表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| repository | ForeignKey | 关联的仓库 |
| filename | String | 文件名 |
| class_name | String | 类名 |
| file_path | Text | 文件路径 |
| imported_at | DateTime | 导入时间 |

## 🔍 测试场景

已有两个测试仓库:
1. **dreamhouse-lwc** - Salesforce示例应用
2. **lwc-recipes** - Lightning Web Components示例(已克隆)

可以测试:
- ✅ 克隆多个仓库
- ✅ 在不同仓库间切换
- ✅ 查看不同仓库的代码结构
- ✅ 删除和重新导入仓库

## 📚 相关文档

- **MULTI_REPO_GUIDE.md** - 详细的实现指南和前端示例代码
- **test_multi_repo.py** - API测试脚本

## 🎨 下一步工作

1. **前端实现** (参考 MULTI_REPO_GUIDE.md)
   - 创建 RepositorySelector 组件
   - 更新主视图集成仓库选择
   - 添加仓库管理页面

2. **功能增强**
   - 添加仓库更新功能(git pull)
   - 支持批量导入
   - 添加仓库标签分类
   - 支持私有仓库(认证)

3. **性能优化**
   - 添加克隆进度显示
   - 优化大型仓库的分析速度
   - 缓存图数据

## 💡 关键提示

1. **仓库名称**: 从Git URL自动提取,例如 `https://github.com/user/repo.git` → `repo`

2. **数据隔离**: 图数据通过 `repository` 属性标识,可以完美支持多仓库

3. **向后兼容**: 旧的AST文件(没有关联仓库)仍然可以正常使用

4. **自动清理**: 删除仓库时会同时删除本地文件和数据库记录

5. **活动仓库**: 同一时间只有一个活动仓库,切换时自动更新

---

**状态**: 后端实现完成 ✅ | 前端待实现 📝

**开发者**: GitHub Copilot
**日期**: 2025-10-27
