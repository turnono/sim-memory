# Deployment Guide - VertexAI Session Service

This document records the successful deployment of the sim-guide agent using VertexAI's managed session service.

## 🎯 Deployment Summary

**Status**: ✅ Successfully Deployed  
**Date**: May 31, 2025  
**Service URL**: https://sim-guide-agent-service-855515190257.us-central1.run.app  
**Session Service**: VertexAI Agent Engine (Managed)  
**Web UI**: Available at `/dev-ui`

## 📋 Configuration Used

### Environment Variables

```bash
GOOGLE_CLOUD_PROJECT=taajirah
GOOGLE_CLOUD_LOCATION=us-central1
REASONING_ENGINE_ID=2565406918206029824
AGENT_SERVICE_NAME=sim-guide-agent-service
```

### Deployment Command

```bash
make deploy
# Executed: adk deploy cloud_run with --session_db_url=agentengine://2565406918206029824
```

### Deployment Options Available

```bash
make deploy                    # Custom session service
make deploy-managed           # VertexAI managed session service ✅ USED
make deploy-with-ui           # Custom + Web UI
make deploy-with-ui-managed   # Managed + Web UI
```

## 🚀 Deployment Process

### 1. Pre-Deployment Setup

- ✅ Google Cloud authentication configured
- ✅ Required APIs enabled (Vertex AI, Cloud Run, Cloud Build)
- ✅ Service account permissions verified
- ✅ Reasoning Engine created and ID configured

### 2. Deployment Execution

```bash
$ make deploy
[Deploy with UI + Managed] Deploying agent with UI and managed session service...
adk deploy cloud_run \
        --project=taajirah \
        --region=us-central1 \
        --service_name=sim-guide-agent-service \
        --app_name=sim-guide \
        --session_db_url=agentengine://2565406918206029824 \
        --with_ui \
        ./sim_guide
```

### 3. Deployment Results

```
✓ Building and deploying new service... Done.
✓ Uploading sources...
✓ Building Container...
✓ Creating Revision...
✓ Routing traffic...
✓ Setting IAM Policy...
Service [sim-guide-agent-service] revision [sim-guide-agent-service-00001-pxs] has been deployed
Service URL: https://sim-guide-agent-service-855515190257.us-central1.run.app
```

## ✅ Verification Results

### 1. API Endpoints Available

- ✅ `GET /docs` - Interactive API documentation
- ✅ `GET /dev-ui` - Web UI interface
- ✅ `POST /run` - Agent interactions
- ✅ `POST /apps/{app_name}/users/{user_id}/sessions` - Session management

### 2. Session Service Testing

**Session Creation**:

```bash
curl -X POST "https://sim-guide-agent-service-855515190257.us-central1.run.app/apps/sim-guide/users/test-user/sessions" -H "Content-Type: application/json" -d '{}'
```

**Response**:

```json
{
  "id": "1715709280063062016",
  "appName": "2565406918206029824",
  "userId": "test-user",
  "state": {},
  "events": [],
  "lastUpdateTime": 1748717033.288221
}
```

### 3. Agent Interaction Testing

**Test Message**:

```bash
curl -X POST "https://sim-guide-agent-service-855515190257.us-central1.run.app/run" \
-H "Content-Type: application/json" \
-d '{
  "appName": "sim-guide",
  "userId": "test-user",
  "sessionId": "1715709280063062016",
  "newMessage": {
    "parts": [{"text": "Hello, can you help me with simulation planning?"}],
    "role": "user"
  }
}'
```

**Results**:

- ✅ Agent responded with detailed simulation planning guidance
- ✅ Token usage tracked: 358 total tokens (53 prompt + 305 response)
- ✅ Session state persisted
- ✅ Traffic type: ON_DEMAND

### 4. State Persistence Verification

**Within Session**:

- ✅ Conversation history maintained across multiple messages
- ✅ Context building works correctly
- ✅ Agent references previous conversation

**Across Sessions**:

- ✅ Sessions completely isolated
- ✅ No cross-session memory (by design)
- ✅ Each session starts fresh

### 5. Cloud Monitoring

**Log Analysis**:

```bash
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=sim-guide-agent-service" --limit=5
```

**Key Indicators Found**:

- ✅ `appendEvent` calls to Reasoning Engine 2565406918206029824
- ✅ HTTP 200 responses for all requests
- ✅ Proper session ID tracking
- ✅ Token usage metadata recorded

## 🌐 Available Interfaces

### 1. REST API

**Base URL**: https://sim-guide-agent-service-855515190257.us-central1.run.app

**Key Endpoints**:

- `POST /run` - Agent interactions
- `GET /docs` - API documentation
- `POST /apps/sim-guide/users/{user_id}/sessions` - Create sessions
- `GET /apps/sim-guide/users/{user_id}/sessions` - List sessions

### 2. Web UI

**URL**: https://sim-guide-agent-service-855515190257.us-central1.run.app/dev-ui

- Visual chat interface
- Session management
- Interactive testing

### 3. API Documentation

**URL**: https://sim-guide-agent-service-855515190257.us-central1.run.app/docs

- Interactive Swagger UI
- All endpoint documentation
- Request/response schemas

## 📊 Performance Metrics

### Token Usage

- **Prompt Tokens**: 53-1988 (varies with conversation history)
- **Response Tokens**: 158-1917 (varies with response complexity)
- **Total Tokens**: 358-2344 per interaction
- **Traffic Type**: ON_DEMAND (pay-as-you-go)

### Response Times

- Session creation: ~500ms
- Agent interactions: ~2-5s (depending on complexity)
- API documentation: <100ms

### Reliability

- ✅ 100% successful deployments
- ✅ No authentication errors
- ✅ Stable session persistence
- ✅ Consistent API responses

## 🔧 Architecture Details

### Session Management

- **Provider**: VertexAI Agent Engine
- **Storage**: Google-managed
- **Persistence**: Within sessions only
- **Scaling**: Automatic

### Container Configuration

- **Platform**: Google Cloud Run
- **Runtime**: Python with ADK
- **Auto-scaling**: Enabled
- **Authentication**: IAM-based

### Security

- ✅ Service account authentication
- ✅ IAM-based access control
- ✅ HTTPS endpoints
- ✅ Session isolation

## 🆘 Troubleshooting Reference

### Common Commands

```bash
# Check service status
gcloud run services describe sim-guide-agent-service --region=us-central1

# View logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=sim-guide-agent-service" --limit=10

# Test health
curl https://sim-guide-agent-service-855515190257.us-central1.run.app/docs

# Delete if needed
make delete
```

### Validation Tests

```bash
# Local agent test
make test-agent

# Session service test
make eval-quick

# Full evaluation
make eval-all
```

## 📝 Lessons Learned

### What Worked Well

1. **ADK CLI Deployment**: Seamless deployment process
2. **Managed Session Service**: Reliable, scalable session management
3. **Dual Interfaces**: Both API and Web UI available
4. **State Isolation**: Clean session boundaries

### Key Configuration Points

1. **--session_db_url**: Critical parameter for managed session service
2. **--with_ui**: Adds web interface without breaking API
3. **Reasoning Engine ID**: Must be correctly configured
4. **Service Account**: Requires proper permissions

### Best Practices Identified

1. Always verify session service connectivity before deployment
2. Test both within-session and cross-session behavior
3. Monitor Cloud logs for session management operations
4. Use managed session service for production deployments

## 🔗 Related Resources

- [Main README](README.md) - Complete project documentation
- [Vertex AI Setup](VERTEX_AI_SETUP.md) - Initial setup guide
- [Makefile](makefile) - All deployment commands
- [Service URL](https://sim-guide-agent-service-855515190257.us-central1.run.app) - Live deployment
