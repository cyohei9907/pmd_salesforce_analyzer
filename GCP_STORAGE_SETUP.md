# GCP Cloud Storage 配置指南

## 概述

本项目现在支持使用 GCP Cloud Storage 来持久化存储数据，包括：
- AST 分析文件
- SQLite 数据库
- 图数据库文件

## 目录结构

```
/data/
├── ast/                    # AST XML 文件
├── database/              # SQLite 数据库文件
│   └── db.sqlite3
└── graph/                 # 图数据库文件
    ├── exports/          # 导出的图数据
    └── graphs/           # 图数据存储
```

## 设置步骤

### 1. 创建 Cloud Storage Bucket

```bash
# 设置项目 ID
export PROJECT_ID=your-project-id

# 创建 bucket（使用与 Cloud Run 相同的区域）
gsutil mb -p $PROJECT_ID -c STANDARD -l asia-northeast1 gs://pmd-salesforce-data/

# 创建目录结构
gsutil -m mkdir -p gs://pmd-salesforce-data/ast/
gsutil -m mkdir -p gs://pmd-salesforce-data/database/
gsutil -m mkdir -p gs://pmd-salesforce-data/graph/exports/
gsutil -m mkdir -p gs://pmd-salesforce-data/graph/graphs/
```

### 2. 设置 IAM 权限

Cloud Run 服务需要访问 Storage bucket 的权限：

```bash
# 获取 Cloud Run 服务账号
SERVICE_ACCOUNT=$(gcloud run services describe pmd-salesforce-analyzer \
  --region=asia-northeast1 \
  --format='value(spec.template.spec.serviceAccountName)')

# 如果没有自定义服务账号，使用默认的
if [ -z "$SERVICE_ACCOUNT" ]; then
  SERVICE_ACCOUNT="${PROJECT_ID}@appspot.gserviceaccount.com"
fi

# 授予 Storage 对象管理员权限
gsutil iam ch serviceAccount:${SERVICE_ACCOUNT}:roles/storage.objectAdmin \
  gs://pmd-salesforce-data
```

### 3. 部署应用

使用 Cloud Build 部署（已配置好 volume 挂载）：

```bash
gcloud builds submit --config=cloudbuild.yaml
```

或手动部署：

```bash
gcloud run deploy pmd-salesforce-analyzer \
  --image=gcr.io/$PROJECT_ID/pmd-salesforce-analyzer:latest \
  --region=asia-northeast1 \
  --platform=managed \
  --memory=1Gi \
  --cpu=1 \
  --timeout=300 \
  --max-instances=5 \
  --min-instances=0 \
  --allow-unauthenticated \
  --set-env-vars=PYTHONUNBUFFERED=1,DEBUG=False,USE_CLOUD_STORAGE=true \
  --add-volume=name=data-volume,type=cloud-storage,bucket=pmd-salesforce-data \
  --add-volume-mount=volume=data-volume,mount-path=/data
```

## 环境变量

| 变量名 | 说明 | 默认值 | 生产环境 |
|--------|------|--------|----------|
| `USE_CLOUD_STORAGE` | 是否使用 Cloud Storage | `false` | `true` |
| `GCS_BUCKET_NAME` | Storage bucket 名称 | `pmd-salesforce-data` | `pmd-salesforce-data` |

## 本地开发

本地开发时，不需要使用 Cloud Storage：

```bash
# 不设置 USE_CLOUD_STORAGE，或设置为 false
export USE_CLOUD_STORAGE=false

# 数据会存储在本地目录
# - backend/db.sqlite3
# - output/ast/
# - graphdata/
```

## 数据迁移

### 从本地迁移到 Cloud Storage

```bash
# 上传 AST 文件
gsutil -m cp -r output/ast/* gs://pmd-salesforce-data/ast/

# 上传数据库（如果需要）
gsutil cp backend/db.sqlite3 gs://pmd-salesforce-data/database/

# 上传图数据（如果存在）
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

## 监控和维护

### 查看 bucket 使用情况

```bash
gsutil du -sh gs://pmd-salesforce-data
```

### 查看目录大小

```bash
gsutil du -sh gs://pmd-salesforce-data/ast/
gsutil du -sh gs://pmd-salesforce-data/database/
gsutil du -sh gs://pmd-salesforce-data/graph/
```

### 清理旧文件

```bash
# 删除特定 AST 文件
gsutil rm gs://pmd-salesforce-data/ast/old_file.xml

# 清空整个目录（谨慎使用）
gsutil -m rm -r gs://pmd-salesforce-data/ast/*
```

## 成本优化

### 生命周期管理

创建生命周期规则来自动删除旧文件：

```bash
# 创建生命周期配置文件 lifecycle.json
cat > lifecycle.json << EOF
{
  "lifecycle": {
    "rule": [
      {
        "action": {"type": "Delete"},
        "condition": {
          "age": 90,
          "matchesPrefix": ["ast/"]
        }
      }
    ]
  }
}
EOF

# 应用生命周期规则
gsutil lifecycle set lifecycle.json gs://pmd-salesforce-data
```

### 存储类别

对于不常访问的数据，可以使用 Nearline 或 Coldline 存储：

```bash
# 将旧文件转为 Nearline 存储
gsutil rewrite -s NEARLINE gs://pmd-salesforce-data/archive/**
```

## 故障排除

### Volume 挂载失败

检查 Cloud Run 服务日志：

```bash
gcloud run services logs read pmd-salesforce-analyzer \
  --region=asia-northeast1 \
  --limit=50
```

### 权限问题

确认服务账号有正确的权限：

```bash
gsutil iam get gs://pmd-salesforce-data
```

### 数据不持久化

1. 确认 `USE_CLOUD_STORAGE=true` 环境变量已设置
2. 确认 volume 正确挂载到 `/data`
3. 检查应用日志中的路径

## 安全建议

1. **访问控制**：使用 IAM 精细控制访问权限
2. **加密**：启用 bucket 加密（默认已启用）
3. **备份**：定期备份重要数据
4. **监控**：设置 Cloud Monitoring 告警

```bash
# 启用 bucket 版本控制（可选）
gsutil versioning set on gs://pmd-salesforce-data
```

## 参考资料

- [Cloud Run Volume Mounts](https://cloud.google.com/run/docs/configuring/services/cloud-storage-volume-mounts)
- [Cloud Storage Documentation](https://cloud.google.com/storage/docs)
- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
