# Cloud Run Deployment Guide

## Prerequisites

1. Google Cloud Platform account
2. `gcloud` CLI installed and configured
3. Enable required APIs:
```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable storage.googleapis.com
```

## Setup

### 1. Create Cloud Storage Bucket for Project Data

```bash
# Set your project ID
export PROJECT_ID=your-project-id

# Create bucket for project data
gsutil mb -p $PROJECT_ID -l asia-northeast1 gs://pmd-salesforce-analyzer-project-data

# Make bucket accessible to Cloud Run
gsutil iam ch allUsers:objectViewer gs://pmd-salesforce-analyzer-project-data
```

### 2. Upload Sample Project (Optional)

```bash
# Upload dreamhouse-lwc project to Cloud Storage
gsutil -m cp -r project/dreamhouse-lwc gs://pmd-salesforce-analyzer-project-data/
```

### 3. Deploy with Cloud Build

```bash
# Submit build
gcloud builds submit --config=cloudbuild.yaml

# Or deploy with custom substitutions
gcloud builds submit \
  --config=cloudbuild.yaml \
  --substitutions=_PROJECT_BUCKET=your-bucket-name
```

## Configuration

### Memory and CPU Settings

The default configuration in `cloudbuild.yaml`:
- **Memory**: 2Gi (suitable for analyzing medium-sized projects)
- **CPU**: 2 vCPU
- **Timeout**: 300 seconds (5 minutes)
- **Max instances**: 10
- **Min instances**: 0 (scales to zero)

Adjust based on your needs:

```yaml
# For larger projects
--memory=4Gi
--cpu=4

# For smaller projects
--memory=1Gi
--cpu=1
```

### Environment Variables

Current settings:
- `PYTHONUNBUFFERED=1` - Real-time log output
- `DEBUG=False` - Production mode
- `PORT=8000` - Application port

Add more variables as needed:
```yaml
--set-env-vars=KEY1=value1,KEY2=value2
```

### Cloud Storage Mount

The project folder is mounted from Cloud Storage:
```yaml
--add-volume=name=project-data,type=cloud-storage,bucket=${_PROJECT_BUCKET}
--add-volume-mount=volume=project-data,mount-path=/app/project
```

This allows:
- Persistent project data across deployments
- Shared access to projects
- Easy project updates via Cloud Storage

## Access the Application

After deployment, Cloud Build will output the service URL:
```
Service URL: https://pmd-salesforce-analyzer-xxxxxxxxxx-an.a.run.app
```

## Monitoring

### View Logs
```bash
gcloud run services logs read pmd-salesforce-analyzer \
  --region=asia-northeast1 \
  --limit=50
```

### View Metrics
```bash
gcloud run services describe pmd-salesforce-analyzer \
  --region=asia-northeast1
```

## Updating

### Update Code
```bash
# Make your changes, then rebuild and redeploy
gcloud builds submit --config=cloudbuild.yaml
```

### Update Environment Variables Only
```bash
gcloud run services update pmd-salesforce-analyzer \
  --region=asia-northeast1 \
  --set-env-vars=NEW_VAR=value
```

### Update Memory/CPU
```bash
gcloud run services update pmd-salesforce-analyzer \
  --region=asia-northeast1 \
  --memory=4Gi \
  --cpu=4
```

## Troubleshooting

### Check Service Status
```bash
gcloud run services describe pmd-salesforce-analyzer \
  --region=asia-northeast1 \
  --format="value(status.url,status.conditions)"
```

### View Recent Logs
```bash
gcloud run services logs tail pmd-salesforce-analyzer \
  --region=asia-northeast1
```

### Test Health Check
```bash
curl https://your-service-url.run.app/
```

## Cost Optimization

- **Auto-scaling**: Set `--min-instances=0` to scale to zero when idle
- **Request timeout**: Adjust `--timeout` based on typical request duration
- **Max instances**: Limit with `--max-instances` to control costs
- **Storage**: Use Cloud Storage lifecycle policies to archive old data

## Security

### Enable Authentication (Optional)
```bash
gcloud run services update pmd-salesforce-analyzer \
  --region=asia-northeast1 \
  --no-allow-unauthenticated
```

### Set IAM Permissions
```bash
# Grant invoker role to specific users
gcloud run services add-iam-policy-binding pmd-salesforce-analyzer \
  --region=asia-northeast1 \
  --member="user:email@example.com" \
  --role="roles/run.invoker"
```

## Clean Up

```bash
# Delete Cloud Run service
gcloud run services delete pmd-salesforce-analyzer \
  --region=asia-northeast1

# Delete Cloud Storage bucket
gsutil rm -r gs://pmd-salesforce-analyzer-project-data

# Delete container images
gcloud container images delete gcr.io/$PROJECT_ID/pmd-salesforce-analyzer --quiet
```
