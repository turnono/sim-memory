# Simulation Guide Agent

A sophisticated AI agent built with Google's Agent Development Kit (ADK) that provides intelligent guidance for simulation planning and optimization. The agent uses VertexAI's managed session service for persistent, context-aware conversations and includes long-term memory capabilities through Vertex AI RAG Engine.

## 🏗️ Architecture

- **Agent Framework**: Google ADK (Agent Development Kit)
- **Session Management**: VertexAI Agent Engine (managed service)
- **Long-term Memory**: Vertex AI RAG Engine for document storage and semantic search
- **Model**: Gemini 2.0 Flash via VertexAI
- **Deployment**: Google Cloud Run
- **Session Persistence**: Conversations maintained within sessions, isolated across sessions
- **Memory Persistence**: Cross-session memory via RAG corpora for user-specific context

## 🧠 RAG Memory Service

The application now includes a comprehensive RAG (Retrieval-Augmented Generation) memory service that provides:

- **Corpus Management**: Create, manage, and delete RAG corpora
- **Document Storage**: Upload simulation guides and reference materials
- **Semantic Search**: Query documents using natural language
- **User Memory**: Store and retrieve user-specific conversation history
- **Integration**: Seamlessly works with the existing session service

### 🚀 RAG Setup

**⚠️ Important**: The RAG Memory Service requires additional setup beyond the basic agent. See the comprehensive setup guide:

**[📖 RAG Setup Guide](RAG_SETUP_GUIDE.md)**

The setup guide covers:

- Enabling Vertex AI APIs
- Configuring service account permissions
- Testing the RAG functionality
- Troubleshooting common issues

## 🚀 Quick Start

### Prerequisites

1. **Google Cloud Project** with billing enabled
2. **Required APIs** enabled:
   - Vertex AI API
   - AI Platform API
   - Cloud Run API
   - Cloud Storage API (for RAG)
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

# 5. Setup RAG Memory Service (optional but recommended)
# Follow the RAG_SETUP_GUIDE.md for complete setup

# 6. Start local development
make dev
```

### Testing the Agent

```bash
# Test agent configuration
make test-agent

# Test RAG memory service (if configured)
make test-rag

# Run evaluation suite
make eval-quick    # Quick health check
make eval-all      # Complete evaluation suite
make eval-rag      # RAG memory tests
```

## 📦 Deployment

### Environment Variables Required

Set these in your `.env` file:

```bash
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1
REASONING_ENGINE_ID=your-reasoning-engine-id
AGENT_SERVICE_NAME=sim-guide-agent-service

# For RAG Memory Service (optional)
PROJECT_ID=your-project-id
LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=./path-to-service-account.json
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

## 📊 Memory Architecture

### Session Management (Short-term)

- **Within Session**: Full conversation history maintained
- **Across Sessions**: Complete isolation (by design)
- **Storage**: VertexAI Agent Engine managed storage

### RAG Memory (Long-term)

- **User-specific Corpora**: Individual memory stores per user
- **Document Storage**: Simulation guides, best practices, reference materials
- **Semantic Retrieval**: Natural language queries to find relevant information
- **Cross-session Continuity**: Remember user preferences and previous simulation contexts

### Memory Lifecycle

1. **Session Create**: New session with unique ID
2. **RAG Initialize**: User corpus created if needed
3. **Interact**: Messages saved to both session and RAG memory
4. **Retrieve**: Relevant memories pulled from RAG when helpful
5. **Persist**: Both session and long-term context maintained

## 🧪 Testing and Evaluation

### Health Checks

```bash
make eval-quick          # Basic health check
make test-session        # Session service test
make test-rag           # RAG memory service test
```

### Full Evaluation Suite

```bash
make eval-all           # Complete evaluation (includes RAG)
make eval-session       # Session functionality tests
make eval-rag           # RAG memory functionality tests
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

# Test RAG health (if configured)
PROJECT_ID=your-project LOCATION=us-central1 python -c "
import asyncio;
from sim_guide.sub_agents.user_context_manager.services.rag_memory_service import health_check;
print(asyncio.run(health_check()))
"
```

## 🔧 Development

### Project Structure

```
sim-memory/
├── sim_guide/              # Agent implementation
│   ├── agent.py            # Main agent configuration
│   ├── session_service.py  # Session service setup
│   └── sub_agents/user_context_manager/services/rag_memory_service.py # RAG memory service
├── evals/                  # Evaluation framework
│   ├── session_evals.py    # Session service tests
│   └── rag_memory_evals.py # RAG memory tests
├── makefile               # Build and deployment commands
├── requirements.txt       # Python dependencies
├── Dockerfile            # Container configuration
├── RAG_SETUP_GUIDE.md    # RAG setup instructions
└── README.md             # This file
```

### Key Files

- `sim_guide/agent.py` - Agent configuration with VertexAI session service
- `sim_guide/sub_agents/user_context_manager/services/rag_memory_service.py` - RAG memory operations and management
- `evals/rag_memory_evals.py` - Comprehensive RAG testing suite
- `RAG_SETUP_GUIDE.md` - Step-by-step RAG configuration guide
- `makefile` - All deployment and testing commands
- `.env` - Environment configuration (create from .env.example)

### ADK Integration

This project uses Google's Agent Development Kit (ADK) with:

- VertexAI session management
- Vertex AI RAG Engine for long-term memory
- Gemini 2.0 Flash model
- Cloud Run deployment

### RAG Memory Integration

The RAG memory service provides seamless integration with:

- **Text Embedding**: Uses `text-embedding-004` model
- **Vector Search**: Semantic similarity search across documents
- **Document Management**: Upload simulation guides, store user conversations
- **Context Augmentation**: Retrieve relevant information to enhance agent responses

## 📋 Available Commands

### Development

- `make dev` - Start local development server
- `make test-agent` - Test agent configuration
- `make test-session` - Test session service
- `make test-rag` - Test RAG memory service

### Evaluation

- `make eval-quick` - Quick health checks
- `make eval-all` - Complete test suite
- `make eval-session` - Session-specific tests
- `make eval-rag` - RAG-specific tests
- `make eval-performance` - Performance benchmarks

### Deployment

- `make deploy` - Deploy to Cloud Run
- `make delete` - Delete deployment
- `make logs` - View deployment logs

## 🔗 Resources

- [Google ADK Documentation](https://cloud.google.com/vertex-ai/generative-ai/docs/agent-development-kit)
- [Vertex AI RAG Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/rag-overview)
- [RAG Setup Guide](RAG_SETUP_GUIDE.md) - **Start here for RAG functionality**
- [Vertex AI Agent Engine](https://cloud.google.com/vertex-ai/generative-ai/docs/agents/overview)

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
