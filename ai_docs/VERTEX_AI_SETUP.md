# VertexAI Session Service Setup & Deployment Guide

This guide walks you through setting up, deploying, and verifying your `sim_guide` agent with Google's managed VertexAI Agent Engine session service.

## 🏗️ Architecture Overview

- **Agent Framework**: Google ADK (Agent Development Kit)
- **Session Management**: VertexAI Agent Engine (managed service)
- **Model**: Gemini 2.0 Flash via VertexAI
- **Deployment**: Google Cloud Run with ADK CLI
- **State Persistence**: Within sessions, isolated across sessions

## 📋 Prerequisites

### 1. Google Cloud Project Setup

- Google Cloud project with billing enabled
- Required APIs enabled:
  - Vertex AI API
  - AI Platform API
  - Cloud Run API
  - Cloud Build API

### 2. Authentication

```bash
# Authenticate with Google Cloud
gcloud auth login
gcloud auth application-default login

# Set default project
gcloud config set project YOUR_PROJECT_ID
```

### 3. Service Account

- Service account configured (`taajirah-agents-service-account.json`)
- Required permissions:
  - Vertex AI User
  - Cloud Run Developer
  - Service Account User

## 🚀 Setup Steps

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements.txt

# Verify ADK installation
python -c "from google import adk; print('ADK installed successfully')"
```

### 2. Environment Configuration

Create `.env` file with required variables:

```bash
# Copy example environment file
cp .env.example .env
```

Required environment variables:

```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
REASONING_ENGINE_ID=your-reasoning-engine-id
AGENT_SERVICE_NAME=sim-guide-agent-service
GOOGLE_GENAI_USE_VERTEXAI=true
```

### 3. Create Reasoning Engine

If you don't have a Reasoning Engine ID, create one:

```bash
# This will create a new Reasoning Engine and return the ID
gcloud ai reasoning-engines create \
  --location=us-central1 \
  --display-name="sim-guide-reasoning-engine"
```

Note the returned ID and add it to your `.env` file as `REASONING_ENGINE_ID`.

## 🚢 Deployment

### Deploy with ADK CLI

The project uses ADK CLI for deployment with multiple options:

#### 1. Standard Deployment (Custom Session Service)

```bash
make deploy
```

#### 2. Managed Session Service (Recommended)

```bash
make deploy-managed
```

Uses VertexAI Agent Engine for session management.

#### 3. With Web UI

```bash
make deploy-with-ui          # Custom session service + UI
make deploy-with-ui-managed  # Managed session service + UI
```

### Deployment Process

1. ADK CLI generates Cloud Run source files
2. Creates Dockerfile automatically
3. Builds and deploys container to Cloud Run
4. Configures session service connection
5. Returns service URL

### Expected Output

```
✓ Building and deploying new service... Done.
✓ Creating Revision...
✓ Routing traffic...
✓ Setting IAM Policy...
Service URL: https://your-service-name-xxx.us-central1.run.app
```

## ✅ Verification & Testing

### 1. Basic Health Check

```bash
# Test agent configuration
make test-agent

# Quick evaluation
make eval-quick
```

### 2. API Testing

Test session creation:

```bash
curl -X POST "https://your-service-url/apps/sim-guide/users/test-user/sessions" \
     -H "Content-Type: application/json" \
     -d '{}'
```

Expected response:

```json
{
  "id": "session-id-here",
  "appName": "your-reasoning-engine-id",
  "userId": "test-user",
  "state": {},
  "events": [],
  "lastUpdateTime": 1748717033.288221
}
```

Test agent interaction:

```bash
curl -X POST "https://your-service-url/run" \
     -H "Content-Type: application/json" \
     -d '{
       "appName": "sim-guide",
       "userId": "test-user",
       "sessionId": "your-session-id",
       "newMessage": {
         "parts": [{"text": "Hello, can you help with simulation planning?"}],
         "role": "user"
       }
     }'
```

### 3. Web UI Testing (if deployed with --with_ui)

Visit: `https://your-service-url/dev-ui`

- Visual chat interface
- Session management
- Interactive testing

### 4. API Documentation

Visit: `https://your-service-url/docs`

- Interactive API documentation
- Test endpoints directly
- View request/response schemas

## 📊 Session Service Verification

### State Persistence Testing

**Within Session (Should Remember):**

```bash
# Send first message
curl -X POST "https://your-service-url/run" -H "Content-Type: application/json" \
-d '{"appName": "sim-guide", "userId": "test", "sessionId": "session-1",
     "newMessage": {"parts": [{"text": "Hello"}], "role": "user"}}'

# Send follow-up (should reference previous message)
curl -X POST "https://your-service-url/run" -H "Content-Type: application/json" \
-d '{"appName": "sim-guide", "userId": "test", "sessionId": "session-1",
     "newMessage": {"parts": [{"text": "What did I just say?"}], "role": "user"}}'
```

**Across Sessions (Should NOT Remember):**

```bash
# Use different session ID - agent should not remember previous session
curl -X POST "https://your-service-url/run" -H "Content-Type: application/json" \
-d '{"appName": "sim-guide", "userId": "test", "sessionId": "session-2",
     "newMessage": {"parts": [{"text": "What did I say earlier?"}], "role": "user"}}'
```

## 📝 Monitoring & Logs

### View Cloud Run Logs

```bash
gcloud logging read \
  "resource.type=cloud_run_revision AND resource.labels.service_name=sim-guide-agent-service" \
  --limit=10 --project=YOUR_PROJECT_ID
```

### Key Log Indicators

Look for these in successful operation:

- `appendEvent` calls to Reasoning Engine
- Token usage metadata
- Session ID tracking
- HTTP 200 responses

### Service Status

```bash
gcloud run services describe sim-guide-agent-service \
  --region=us-central1 --project=YOUR_PROJECT_ID
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Authentication Errors

```bash
# Re-authenticate
gcloud auth login
gcloud auth application-default login

# Check current auth
gcloud auth list
```

#### 2. Missing Reasoning Engine

```bash
# List existing reasoning engines
gcloud ai reasoning-engines list --location=us-central1

# Create new one if needed
gcloud ai reasoning-engines create --location=us-central1 --display-name="sim-guide"
```

#### 3. API Errors

- Verify APIs are enabled
- Check service account permissions
- Ensure billing is enabled

#### 4. Session Service Issues

```bash
# Test session connectivity
make test-session

# Run comprehensive evaluation
make eval-all
```

#### 5. Deployment Failures

- Check `REASONING_ENGINE_ID` is correct
- Verify all required environment variables
- Ensure Docker is running (for local builds)

### Debug Commands

```bash
# Test local agent configuration
python -c "from sim_guide.agent import root_agent; print(f'Agent: {root_agent.name}')"

# Test session service
python -c "from sim_guide.session_service import health_check; import asyncio; print(asyncio.run(health_check()))"
```

## 🧹 Cleanup

### Delete Deployment

```bash
make delete
```

### Manual Cleanup

```bash
# Delete Cloud Run service
gcloud run services delete sim-guide-agent-service --region=us-central1

# Delete Reasoning Engine (if no longer needed)
gcloud ai reasoning-engines delete YOUR_REASONING_ENGINE_ID --location=us-central1
```

## 📚 Additional Resources

- [Google ADK Documentation](https://cloud.google.com/vertex-ai/docs/agent-development-kit)
- [Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/docs/reasoning-engines)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Project README](README.md) - Complete project documentation
