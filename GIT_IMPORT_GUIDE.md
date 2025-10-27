# Git 仓库导入功能说明

## 功能概述

现在系统支持直接从 Git 仓库导入 Salesforce 项目并自动分析。

## 架构变更

### 后端新增

1. **git_service.py** - Git 仓库管理服务
   - `clone_repository()` - 克隆 Git 仓库
   - `analyze_repository()` - 使用 PMD 分析 Apex 代码
   - `list_repositories()` - 列出已克隆的仓库
   - `delete_repository()` - 删除仓库

2. **新增 API 端点**:
   - `POST /api/git/clone/` - 克隆仓库
   - `POST /api/git/analyze/` - 分析仓库
   - `POST /api/git/clone-and-analyze/` - 一键克隆并分析
   - `GET /api/git/repositories/` - 列出仓库
   - `DELETE /api/git/repositories/<name>/` - 删除仓库

### 前端新增

1. **ImportData.vue** - 新增"从Git仓库导入"选项卡
   - Git 仓库 URL 输入
   - 分支选择
   - Apex 代码路径配置
   - 自动导入选项
   - 强制覆盖选项

2. **API 客户端** - 新增 Git 相关方法
   - `cloneRepository()`
   - `analyzeRepository()`
   - `cloneAndAnalyze()`
   - `listRepositories()`
   - `deleteRepository()`

## 使用方法

### 1. 通过 UI 导入

1. 访问"导入 AST 数据"页面
2. 切换到"从Git仓库导入"选项卡
3. 输入 Git 仓库 URL（例如：https://github.com/trailheadapps/dreamhouse-lwc.git）
4. 配置选项：
   - **分支**: 默认 `main`
   - **Apex代码路径**: 默认 `force-app/main/default/classes`
   - **自动导入**: 勾选后分析完成自动导入到图数据库
   - **强制覆盖**: 如果仓库已存在，是否覆盖
5. 点击"克隆并分析"按钮

### 2. 通过 API 导入

```bash
# 一键克隆、分析并导入
curl -X POST https://your-cloudrun-url/api/git/clone-and-analyze/ \
  -H "Content-Type: application/json" \
  -d '{
    "repo_url": "https://github.com/trailheadapps/dreamhouse-lwc.git",
    "branch": "main",
    "apex_dir": "force-app/main/default/classes",
    "auto_import": true,
    "force": false
  }'
```

## 工作流程

1. **克隆仓库**
   - 从 Git URL 克隆到 `/app/project/<repo_name>/`
   - 支持指定分支
   - 使用 `--depth 1` 进行浅克隆以节省空间

2. **分析 Apex 代码**
   - 查找指定目录中的 `.cls` 文件
   - 对每个文件运行 PMD AST 分析
   - 生成 AST 文件到 `/app/output/ast/`

3. **自动导入（可选）**
   - 调用现有的导入服务
   - 将 AST 数据导入图数据库
   - 更新统计信息

## 支持的仓库结构

系统会自动检测以下常见的 Salesforce 项目结构：

- `force-app/main/default/classes/` (SFDX 标准)
- `src/classes/` (旧版结构)
- `classes/` (简化结构)

## 注意事项

1. **容器存储**: 克隆的仓库存储在容器中，容器重启后会丢失
2. **超时设置**: 
   - Git 克隆: 5 分钟超时
   - PMD 分析: 每个文件 1 分钟超时
3. **权限**: 目前仅支持公开仓库，私有仓库需要配置 Git 认证

## 未来改进

1. 支持私有仓库（SSH 密钥或访问令牌）
2. 集成 Cloud Storage 持久化仓库
3. 增量更新（git pull）而不是每次重新克隆
4. 支持更多代码分析工具
5. 批量导入多个仓库

## 示例仓库

可以使用以下公开仓库测试：

1. Dreamhouse LWC
   - URL: `https://github.com/trailheadapps/dreamhouse-lwc.git`
   - 路径: `force-app/main/default/classes`

2. E-Bikes LWC
   - URL: `https://github.com/trailheadapps/ebikes-lwc.git`
   - 路径: `force-app/main/default/classes`
