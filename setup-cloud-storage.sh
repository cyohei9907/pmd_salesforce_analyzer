#!/bin/bash
# GCP Cloud Storage 部署准备脚本

set -e

echo "=== PMD Salesforce Analyzer - Cloud Storage Setup ==="
echo ""

# 检查是否设置了 PROJECT_ID
if [ -z "$PROJECT_ID" ]; then
    echo "请设置 PROJECT_ID 环境变量"
    echo "例如: export PROJECT_ID=your-project-id"
    exit 1
fi

BUCKET_NAME="pmd-salesforce-data"
REGION="asia-northeast1"

echo "Project ID: $PROJECT_ID"
echo "Bucket Name: $BUCKET_NAME"
echo "Region: $REGION"
echo ""

# 1. 检查 bucket 是否已存在
echo "步骤 1: 检查 Cloud Storage bucket..."
if gsutil ls -b gs://$BUCKET_NAME &>/dev/null; then
    echo "✓ Bucket gs://$BUCKET_NAME 已存在"
else
    echo "创建 bucket gs://$BUCKET_NAME..."
    gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$BUCKET_NAME/
    echo "✓ Bucket 创建成功"
fi
echo ""

# 2. 创建目录结构
echo "步骤 2: 创建目录结构..."
echo "创建 /ast/ 目录..."
gsutil -m mkdir -p gs://$BUCKET_NAME/ast/ 2>/dev/null || true

echo "创建 /database/ 目录..."
gsutil -m mkdir -p gs://$BUCKET_NAME/database/ 2>/dev/null || true

echo "创建 /graph/ 目录..."
gsutil -m mkdir -p gs://$BUCKET_NAME/graph/exports/ 2>/dev/null || true
gsutil -m mkdir -p gs://$BUCKET_NAME/graph/graphs/ 2>/dev/null || true

echo "✓ 目录结构创建完成"
echo ""

# 3. 设置 IAM 权限
echo "步骤 3: 配置 IAM 权限..."

# 检查 Cloud Run 服务是否存在
if gcloud run services describe pmd-salesforce-analyzer --region=$REGION &>/dev/null; then
    SERVICE_ACCOUNT=$(gcloud run services describe pmd-salesforce-analyzer \
      --region=$REGION \
      --format='value(spec.template.spec.serviceAccountName)' 2>/dev/null || echo "")
    
    if [ -z "$SERVICE_ACCOUNT" ]; then
        SERVICE_ACCOUNT="${PROJECT_ID}@appspot.gserviceaccount.com"
        echo "使用默认服务账号: $SERVICE_ACCOUNT"
    else
        echo "使用自定义服务账号: $SERVICE_ACCOUNT"
    fi
    
    echo "授予 Storage 访问权限..."
    gsutil iam ch serviceAccount:${SERVICE_ACCOUNT}:roles/storage.objectAdmin \
      gs://$BUCKET_NAME
    echo "✓ IAM 权限配置完成"
else
    echo "⚠ Cloud Run 服务尚未部署，跳过 IAM 配置"
    echo "  部署后请运行以下命令配置权限："
    echo "  gsutil iam ch serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com:roles/storage.objectAdmin gs://$BUCKET_NAME"
fi
echo ""

# 4. 可选：上传示例数据
echo "步骤 4: 上传示例数据（可选）..."
read -p "是否上传本地 output/ast/ 中的示例数据? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -d "output/ast" ] && [ "$(ls -A output/ast)" ]; then
        echo "上传 AST 示例文件..."
        gsutil -m cp -r output/ast/* gs://$BUCKET_NAME/ast/
        echo "✓ 示例数据上传完成"
    else
        echo "⚠ output/ast/ 目录为空或不存在"
    fi
else
    echo "跳过示例数据上传"
fi
echo ""

# 5. 验证配置
echo "步骤 5: 验证配置..."
echo "Bucket 内容:"
gsutil ls gs://$BUCKET_NAME/
echo ""
echo "✓ Cloud Storage 配置完成！"
echo ""

# 6. 显示部署命令
echo "=== 下一步 ==="
echo "运行以下命令部署应用到 Cloud Run:"
echo ""
echo "gcloud builds submit --config=cloudbuild.yaml"
echo ""
echo "或手动部署:"
echo ""
echo "gcloud run deploy pmd-salesforce-analyzer \\"
echo "  --image=gcr.io/$PROJECT_ID/pmd-salesforce-analyzer:latest \\"
echo "  --region=$REGION \\"
echo "  --platform=managed \\"
echo "  --memory=1Gi \\"
echo "  --cpu=1 \\"
echo "  --timeout=300 \\"
echo "  --max-instances=5 \\"
echo "  --min-instances=0 \\"
echo "  --allow-unauthenticated \\"
echo "  --set-env-vars=PYTHONUNBUFFERED=1,DEBUG=False,USE_CLOUD_STORAGE=true \\"
echo "  --add-volume=name=data-volume,type=cloud-storage,bucket=$BUCKET_NAME \\"
echo "  --add-volume-mount=volume=data-volume,mount-path=/data"
echo ""
