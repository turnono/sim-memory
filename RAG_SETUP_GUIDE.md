# Vertex AI RAG Memory Service Setup Guide

This guide provides step-by-step instructions to set up the Vertex AI RAG Memory Service for the sim-memory application.

## Prerequisites

1. **Google Cloud Project**: You need a Google Cloud project with billing enabled
2. **Service Account**: A service account with proper permissions (we'll set this up)
3. **Environment**: Python 3.8+ with the required dependencies installed

## Step 1: Enable Required APIs

Enable the necessary Google Cloud APIs for your project:

```bash
# Enable Vertex AI API
gcloud services enable aiplatform.googleapis.com

# Enable Cloud Storage API (for document storage)
gcloud services enable storage.googleapis.com

# Enable Cloud Resource Manager API (for project management)
gcloud services enable cloudresourcemanager.googleapis.com

# Verify APIs are enabled
gcloud services list --enabled --filter="name:(aiplatform.googleapis.com OR storage.googleapis.com)"
```

## Step 2: Configure Service Account Permissions

The existing service account (`taajirah-agents-service-account`) needs additional permissions for RAG operations:

```bash
# Get your project ID
PROJECT_ID=$(gcloud config get-value project)

# Add Vertex AI Administrator role (includes all RAG permissions)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:taajirah-agents-service-account@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.admin"

# Add Storage Admin role (for document uploads)
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:taajirah-agents-service-account@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/storage.admin"
```

### Alternative: Minimal Permissions (More Secure)

If you prefer minimal permissions instead of admin roles:

```bash
# Create a custom role with specific RAG permissions
gcloud iam roles create ragMemoryServiceRole \
    --project=$PROJECT_ID \
    --title="RAG Memory Service Role" \
    --description="Minimal permissions for RAG memory operations" \
    --permissions="aiplatform.ragCorpora.create,aiplatform.ragCorpora.delete,aiplatform.ragCorpora.get,aiplatform.ragCorpora.list,aiplatform.ragCorpora.query,aiplatform.ragFiles.import,aiplatform.ragFiles.upload,aiplatform.ragFiles.get,aiplatform.ragFiles.list,aiplatform.ragFiles.delete,storage.buckets.create,storage.buckets.get,storage.buckets.list,storage.objects.create,storage.objects.get,storage.objects.list,storage.objects.delete"

# Assign the custom role
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:taajirah-agents-service-account@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="projects/$PROJECT_ID/roles/ragMemoryServiceRole"
```

## Step 3: Verify Service Account Key

Ensure your service account key file is properly placed:

```bash
# Check if the service account key exists
ls -la taajirah-agents-service-account.json

# Verify the service account can authenticate
gcloud auth activate-service-account --key-file=taajirah-agents-service-account.json
gcloud auth list
```

## Step 4: Set Environment Variables

Create a `.env` file or set environment variables:

```bash
# Set required environment variables
export PROJECT_ID="taajirah-agents"
export LOCATION="us-central1"
export GOOGLE_APPLICATION_CREDENTIALS="./taajirah-agents-service-account.json"

# Optional: Add to .env file
echo "PROJECT_ID=taajirah-agents" > .env
echo "LOCATION=us-central1" >> .env
echo "GOOGLE_APPLICATION_CREDENTIALS=./taajirah-agents-service-account.json" >> .env
```

## Step 5: Test the Setup

Run the RAG memory service health check to verify everything is working:

```bash
# Run health check
PROJECT_ID=taajirah-agents LOCATION=us-central1 python -c "
import asyncio
import sys
sys.path.append('.')
from sim_guide.rag_memory_service import health_check
result = asyncio.run(health_check())
print('Health Check Result:', result)
if result['status'] == 'healthy':
    print('✅ RAG Memory Service is ready!')
else:
    print('❌ Setup incomplete. Check the logs above.')
"
```

## Step 6: Run Full Evaluation (Optional)

Once the health check passes, you can run the full evaluation suite:

```bash
# Run comprehensive tests
PROJECT_ID=taajirah-agents LOCATION=us-central1 python -m evals.rag_memory_evals
```

## Troubleshooting

### Permission Denied Errors

If you see "Permission denied" errors:

1. **Check API enablement**:

   ```bash
   gcloud services list --enabled --filter="name:aiplatform.googleapis.com"
   ```

2. **Verify service account permissions**:

   ```bash
   gcloud projects get-iam-policy $PROJECT_ID \
       --flatten="bindings[].members" \
       --filter="bindings.members:taajirah-agents-service-account@$PROJECT_ID.iam.gserviceaccount.com"
   ```

3. **Check service account key**:
   ```bash
   gcloud auth activate-service-account --key-file=taajirah-agents-service-account.json
   ```

### Region/Location Issues

Vertex AI RAG Engine is available in specific regions. Supported regions:

- `us-central1` (Iowa) - GA
- `europe-west3` (Frankfurt) - GA
- `us-east4` (Virginia) - Preview
- `europe-west4` (Netherlands) - Preview

If you need to use a different region, update the `LOCATION` environment variable.

### Quota Limits

If you encounter quota issues:

1. **Check current quotas**:

   ```bash
   gcloud compute project-info describe --project=$PROJECT_ID
   ```

2. **Request quota increases** through the Google Cloud Console if needed

## Features Overview

Once set up, the RAG Memory Service provides:

- **Corpus Management**: Create, list, update, and delete RAG corpora
- **Document Management**: Upload documents to Cloud Storage and import to RAG corpora
- **Querying**: Search specific corpora or across all corpora with semantic similarity
- **Memory Storage**: Store and retrieve user conversation memories
- **Integration**: Works with existing sim-memory session service

## Next Steps

After successful setup:

1. **Integrate with your application**: Use the RAG memory service functions in your simulation guidance application
2. **Customize memory types**: Extend memory categorization for different simulation contexts
3. **Optimize performance**: Adjust similarity thresholds and top-k parameters based on your use case
4. **Monitor usage**: Track RAG API usage and costs in Google Cloud Console

## Support

If you encounter issues:

1. Check the [Vertex AI RAG Engine documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-overview)
2. Review the evaluation logs for specific error messages
3. Verify all prerequisites are met
4. Contact Google Cloud support for quota or API issues
