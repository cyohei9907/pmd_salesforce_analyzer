# Cloud Storage 集成更新说明

## 更新内容

### 1. 新增文件

- **backend/cloud_storage.py**: Cloud Storage 配置和路径管理
- **GCP_STORAGE_SETUP.md**: 完整的 Cloud Storage 配置指南
- **setup-cloud-storage.sh**: 自动化设置脚本

### 2. 文件修改

#### backend/apex_graph/settings.py
- 添加 `USE_CLOUD_STORAGE` 环境变量支持
- 数据库路径根据环境自动切换
  - 本地开发: `backend/db.sqlite3`
  - Cloud Storage: `/data/database/db.sqlite3`

#### backend/ast_api/git_service.py
- AST 输出目录支持 Cloud Storage
  - 本地开发: `output/ast/`
  - Cloud Storage: `/data/ast/`

#### backend/ast_api/views.py
- 自动导入功能支持 Cloud Storage 路径

#### Dockerfile
- 创建 `/data` 目录结构
- 复制 `cloud_storage.py` 配置文件

#### docker-entrypoint.sh
- 自动初始化 Cloud Storage 目录
- 首次启动时复制示例 AST 文件

#### cloudbuild.yaml
- 添加 `USE_CLOUD_STORAGE=true` 环境变量
- 配置 Cloud Storage volume 挂载

## 新的目录结构

### 生产环境 (Cloud Storage)
```
/data/                          # Cloud Storage 挂载点
├── ast/                        # AST XML 文件
│   ├── FileUtilities_ast.xml
│   └── ...
├── database/                   # SQLite 数据库
│   └── db.sqlite3
└── graph/                      # 图数据库
    ├── exports/                # 导出文件
    └── graphs/                 # 图数据
```

### 本地开发
```
backend/
├── db.sqlite3                  # SQLite 数据库

output/
└── ast/                        # AST XML 文件
    ├── FileUtilities_ast.xml
    └── ...

graphdata/
├── exports/                    # 导出文件
└── graphs/                     # 图数据
```

## 环境变量

| 变量 | 本地开发 | 生产环境 | 说明 |
|------|---------|---------|------|
| `USE_CLOUD_STORAGE` | `false` (默认) | `true` | 是否使用 Cloud Storage |
| `GCS_BUCKET_NAME` | - | `pmd-salesforce-data` | Bucket 名称 |

## 部署步骤

### 首次部署

1. **设置项目 ID**
   ```bash
   export PROJECT_ID=your-project-id
   ```

2. **运行 Cloud Storage 设置脚本**
   ```bash
   chmod +x setup-cloud-storage.sh
   ./setup-cloud-storage.sh
   ```

3. **构建和部署**
   ```bash
   gcloud builds submit --config=cloudbuild.yaml
   ```

### 后续部署

直接运行 Cloud Build：
```bash
gcloud builds submit --config=cloudbuild.yaml
```

## 数据迁移

### 从本地上传到 Cloud Storage

```bash
# 上传 AST 文件
gsutil -m cp -r output/ast/* gs://pmd-salesforce-data/ast/

# 上传数据库
gsutil cp backend/db.sqlite3 gs://pmd-salesforce-data/database/

# 上传图数据
gsutil -m cp -r graphdata/* gs://pmd-salesforce-data/graph/
```

### 从 Cloud Storage 下载到本地

```bash
# 下载 AST 文件
gsutil -m cp -r gs://pmd-salesforce-data/ast/* output/ast/

# 下载数据库
gsutil cp gs://pmd-salesforce-data/database/db.sqlite3 backend/

# 下载图数据
gsutil -m cp -r gs://pmd-salesforce-data/graph/* graphdata/
```

## 本地测试

本地开发不需要任何改动，所有路径自动使用本地目录：

```bash
# 启动后端
cd backend
python manage.py runserver

# 启动前端
cd frontend
pnpm dev
```

## 验证部署

部署成功后，检查以下内容：

1. **环境变量**
   ```bash
   gcloud run services describe pmd-salesforce-analyzer \
     --region=asia-northeast1 \
     --format='value(spec.template.spec.containers[0].env)'
   ```
   应该看到 `USE_CLOUD_STORAGE=true`

2. **Volume 挂载**
   ```bash
   gcloud run services describe pmd-salesforce-analyzer \
     --region=asia-northeast1 \
     --format='value(spec.template.spec.volumes)'
   ```
   应该看到 volume 配置

3. **应用日志**
   ```bash
   gcloud run services logs read pmd-salesforce-analyzer \
     --region=asia-northeast1 \
     --limit=50
   ```
   应该看到 "Cloud Storage directories initialized"

## 故障排除

### 问题: Volume 挂载失败

**症状**: 日志中看到 permission denied 错误

**解决方案**:
```bash
# 检查 IAM 权限
gsutil iam get gs://pmd-salesforce-data

# 重新授权
SERVICE_ACCOUNT=$(gcloud run services describe pmd-salesforce-analyzer \
  --region=asia-northeast1 \
  --format='value(spec.template.spec.serviceAccountName)')
  
gsutil iam ch serviceAccount:${SERVICE_ACCOUNT}:roles/storage.objectAdmin \
  gs://pmd-salesforce-data
```

### 问题: 数据不持久化

**症状**: 重启后数据丢失

**检查清单**:
1. ✅ `USE_CLOUD_STORAGE=true` 已设置
2. ✅ Volume 正确挂载到 `/data`
3. ✅ 应用日志显示使用 Cloud Storage
4. ✅ Bucket 有写入权限

### 问题: 本地开发连接到 Cloud Storage

**症状**: 本地测试时尝试访问 `/data` 目录

**解决方案**: 确保本地没有设置 `USE_CLOUD_STORAGE` 环境变量

## 成本估算

### Cloud Storage 费用

- **存储**: $0.020 per GB/month (Standard, asia-northeast1)
- **操作**: 
  - Class A (写入): $0.05 per 10,000 operations
  - Class B (读取): $0.004 per 10,000 operations

### 预估成本 (每月)

假设场景:
- 存储数据: 5 GB
- AST 文件写入: 10,000 次
- 文件读取: 100,000 次

费用:
- 存储: 5 GB × $0.020 = $0.10
- 写入: 10,000 / 10,000 × $0.05 = $0.05
- 读取: 100,000 / 10,000 × $0.004 = $0.04

**总计约 $0.19/月**

## 备份建议

定期备份 bucket 数据：

```bash
# 创建备份脚本
cat > backup-cloud-storage.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d)
BACKUP_BUCKET="pmd-salesforce-data-backup"

echo "Backing up to gs://$BACKUP_BUCKET/$DATE/"
gsutil -m rsync -r gs://pmd-salesforce-data/ gs://$BACKUP_BUCKET/$DATE/
echo "Backup completed"
EOF

chmod +x backup-cloud-storage.sh
```

## 参考文档

详细配置说明请查看:
- [GCP_STORAGE_SETUP.md](./GCP_STORAGE_SETUP.md) - 完整配置指南
- [Cloud Run Volume Mounts](https://cloud.google.com/run/docs/configuring/services/cloud-storage-volume-mounts)
