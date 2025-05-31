# Simulation Guide Agent

A sophisticated AI agent built with Google's Agent Development Kit (ADK) that provides intelligent guidance for simulation planning and optimization. The agent uses VertexAI's managed session service for persistent, context-aware conversations.

## 🏗️ Architecture

- **Agent Framework**: Google ADK (Agent Development Kit)
- **Session Management**: VertexAI Agent Engine (managed service)
- **Model**: Gemini 2.0 Flash via VertexAI
- **Deployment**: Google Cloud Run
- **Session Persistence**: Conversations maintained within sessions, isolated across sessions

## 🚀 Quick Start

### Prerequisites

1. **Google Cloud Project** with billing enabled
2. **Required APIs** enabled:
   - Vertex AI API
   - AI Platform API
   - Cloud Run API
3. **Authentication**: `gcloud auth login` and `gcloud auth application-default login`

### Local Development

```bash
# 1. Clone and setup
git clone <repository>
cd sim-memory

# 2. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables (see .env.example)
cp .env.example .env
# Edit .env with your Google Cloud project details

# 5. Start local development
make dev
```

### Testing the Agent

```bash
# Test agent configuration
make test-agent

# Run evaluation suite
make eval-quick    # Quick health check
make eval-all      # Complete evaluation suite
```

## 📦 Deployment

### Environment Variables Required

Set these in your `.env` file:

```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
REASONING_ENGINE_ID=your-reasoning-engine-id
AGENT_SERVICE_NAME=sim-guide-agent-service
```

### Deploy with ADK CLI

```bash
# Standard deployment
make deploy

```

### Delete Deployment

```bash
make delete
```

## 🌐 Usage

Once deployed, your agent is available via:

### 1. REST API

**Base URL**: `https://your-service-url.run.app`

**Key Endpoints**:

- `POST /run` - Agent interactions
- `GET /docs` - Interactive API documentation
- `POST /apps/{app_name}/users/{user_id}/sessions` - Create sessions
- `GET /apps/{app_name}/users/{user_id}/sessions` - List sessions

**Example API Usage**:

```bash
# Create a session
curl -X POST "https://your-service-url/apps/sim-guide/users/test-user/sessions" \
     -H "Content-Type: application/json" -d '{}'

# Send a message
curl -X POST "https://your-service-url/run" \
     -H "Content-Type: application/json" \
     -d '{
       "appName": "sim-guide",
       "userId": "test-user",
       "sessionId": "your-session-id",
       "newMessage": {
         "parts": [{"text": "Help me plan a simulation study"}],
         "role": "user"
       }
     }'
```

### 2. Web UI (if deployed with --with_ui)

**URL**: `https://your-service-url.run.app/dev-ui`

- Visual chat interface
- Session management
- Easy testing and demos

## 📊 Session Management

### State Persistence

- **Within Session**: Full conversation history maintained
- **Across Sessions**: Complete isolation (by design)
- **Storage**: VertexAI Agent Engine managed storage

### Session Lifecycle

1. **Create**: New session with unique ID
2. **Interact**: Messages append to session history
3. **Persist**: Context maintained across requests
4. **Isolate**: No cross-session memory

## 🧪 Testing and Evaluation

### Health Checks

```bash
make eval-quick          # Basic health check
make test-session        # Session service test
```

### Full Evaluation Suite

```bash
make eval-all           # Complete evaluation
make eval-session       # Session functionality tests
make eval-agent         # Agent behavior tests
make eval-performance   # Performance tests
```

### Manual Testing

```bash
# Test deployed service health
curl https://your-service-url.run.app/docs

# Test session creation
curl -X POST "https://your-service-url.run.app/apps/sim-guide/users/test/sessions" \
     -H "Content-Type: application/json" -d '{}'
```

## 🔧 Development

### Project Structure

```
sim-memory/
├── sim_guide/          # Agent implementation
│   ├── agent.py        # Main agent configuration
│   └── session_service.py # Session service setup
├── evals/              # Evaluation framework
├── makefile           # Build and deployment commands
├── requirements.txt   # Python dependencies
├── Dockerfile        # Container configuration
└── README.md         # This file
```

### Key Files

- `sim_guide/agent.py` - Agent configuration with VertexAI session service
- `makefile` - All deployment and testing commands
- `.env` - Environment configuration (create from .env.example)

### ADK Integration

This project uses Google's Agent Development Kit (ADK) with:

- VertexAI session management
- Gemini 2.0 Flash model
- Cloud Run deployment
- Built-in evaluation framework

## 📝 Monitoring

### View Logs

```bash
# Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=sim-guide-agent-service" --limit=10

# Service status
gcloud run services describe sim-guide-agent-service --region=us-central1
```

### Key Metrics

- Token usage (prompt + response tokens)
- Session creation/management
- API response times
- Error rates

## 🔗 Related Documentation

- [Vertex AI Setup Guide](VERTEX_AI_SETUP.md) - Initial VertexAI configuration
- [Google ADK Documentation](https://cloud.google.com/vertex-ai/docs/agent-development-kit)
- [API Documentation](https://your-service-url.run.app/docs) - Interactive API docs

## 🆘 Troubleshooting

### Common Issues

1. **Authentication Errors**

   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```

2. **Missing Environment Variables**

   - Check `.env` file configuration
   - Verify Google Cloud project settings

3. **Deployment Failures**

   - Ensure required APIs are enabled
   - Check service account permissions
   - Verify `REASONING_ENGINE_ID` is correct

4. **Session Service Issues**
   ```bash
   make test-session  # Test session connectivity
   make eval-quick    # Quick health check
   ```

## 📄 License

This project is licensed under the Apache License 2.0.
