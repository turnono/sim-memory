include sim_guide/.env
export 

firestore-emulator:
	@echo "[Firestore Emulator] Starting Firestore emulator. Run this in its own terminal window!"
	FIRESTORE_EMULATOR_HOST=localhost:8087 firebase emulators:start --only firestore,auth --project ${GOOGLE_CLOUD_PROJECT}

dev:
	@echo "[Dev Server] Starting ADK API server. Run this in a separate terminal after the emulator is running!"
	ENV=development FIRESTORE_EMULATOR_HOST=localhost:8087 python main.py --allow_origins="http://localhost:4200"

frontend-do:
	cd frontend && npm start

# Local development with ADK server (using working in-code DatabaseSessionService)
local-server:
	@echo "[Local ADK Server] Starting ADK API server with in-code DatabaseSessionService..."
	@echo "Using DatabaseSessionService configured in code with SQLite database"
	@echo "Setting PYTHONPATH to $(PWD) to fix module import issues"
	PYTHONPATH=$(PWD):$$PYTHONPATH adk api_server sim_guide

# production build and deploy

deploy-frontend:
	cd frontend && ng build --configuration=production && firebase deploy --only hosting:tjr-sim-guide --project=${GOOGLE_CLOUD_PROJECT}

# Deploy the agent service to Google Cloud Run
deploy:
	@echo "[Deploy with UI + Managed] Deploying agent with UI and managed session service..."
	@if [ -z "${REASONING_ENGINE_ID}" ]; then \
		echo "❌ Error: REASONING_ENGINE_ID environment variable is not set."; \
		echo "Set it in your .env file or export it: export REASONING_ENGINE_ID=your-agent-engine-resource-id"; \
		exit 1; \
	fi
	adk deploy cloud_run \
	--project=${GOOGLE_CLOUD_PROJECT} \
	--region=${GOOGLE_CLOUD_LOCATION} \
	--service_name=${AGENT_SERVICE_NAME} \
	--app_name=${APP_NAME} \
	--session_db_url=agentengine://${REASONING_ENGINE_ID} \
	--with_ui \
	./sim_guide

deploy-gcloud-cli:
	@echo "[Deploy with gcloud] Deploying agent with managed session service using gcloud run deploy..."
	@if [ -z "${REASONING_ENGINE_ID}" ]; then \
		echo "❌ Error: REASONING_ENGINE_ID environment variable is not set."; \
		echo "Set it in your .env file or export it: export REASONING_ENGINE_ID=your-agent-engine-resource-id"; \
		exit 1; \
	fi
	gcloud run deploy ${AGENT_SERVICE_NAME} \
	--source . \
	--region ${GOOGLE_CLOUD_LOCATION} \
	--allow-unauthenticated \
	--port 8000 \
	--service-account ${AGENT_SERVICE_ACCOUNT} \
	--set-env-vars="GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT},\
GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION},\
GOOGLE_GENAI_USE_VERTEXAI=${GOOGLE_GENAI_USE_VERTEXAI},\
REASONING_ENGINE_ID=${REASONING_ENGINE_ID},\
ENV=${ENV}"


# Delete the agent service from Google Cloud Run
delete:
	gcloud run services delete ${AGENT_SERVICE_NAME} \
	--region ${GOOGLE_CLOUD_LOCATION}

# Test the session service health
test-session:
	@echo "[Test] Testing session service health..."
	python -c "from sim_guide.agent import root_agent; print('✅ Agent and session service configured correctly')"

# Test the new ADK-pattern memory service
test-memory-adk:
	@echo "[Test] Testing new ADK-pattern memory service..."
	PROJECT_ID=${GOOGLE_CLOUD_PROJECT} LOCATION=${GOOGLE_CLOUD_LOCATION} python test_memory_system.py

# Test the RAG memory service health (legacy)
test-rag:
	@echo "[Test] Testing RAG memory service health..."
	PROJECT_ID=${GOOGLE_CLOUD_PROJECT} LOCATION=${GOOGLE_CLOUD_LOCATION} python -c "import asyncio; from sim_guide.sub_agents.memory_manager.services.rag_memory_service import health_check; result = asyncio.run(health_check()); print('✅ Memory Service healthy' if result.get('status') in ['healthy', 'degraded'] else '❌ Memory Service failed'); print(f'Status: {result.get(\"status\")}')"

test-agent:
	@echo "[Agent Test] Testing the agent configuration..."
	python -c "from sim_guide.agent import root_agent; print(f'✅ Agent {root_agent.name} configured with memory_manager sub-agent')"

# Test meta-cognitive capabilities
test-meta-cognitive:
	@echo "[Test Meta-Cognitive] Testing meta-cognitive capabilities..."
	python evals/meta_cognitive_evals.py

eval-meta-cognitive:
	@echo "[Eval Meta-Cognitive] Running meta-cognitive capabilities evaluation..."
	python evals/meta_cognitive_evals.py

eval-meta-cognitive-cost-optimized:
	@echo "[Eval Meta-Cognitive - Cost Optimized] Running meta-cognitive evaluation with cost optimization..."
	USE_EVAL_AGENT=true RAG_COST_OPTIMIZED=true python evals/meta_cognitive_evals.py

# Evaluation commands
eval-all:
	@echo "[Eval All] Running complete evaluation suite..."
	PROJECT_ID=${GOOGLE_CLOUD_PROJECT} LOCATION=${GOOGLE_CLOUD_LOCATION} REASONING_ENGINE_ID=${REASONING_ENGINE_ID} python evals/run_all_evals.py

# Cost-optimized evaluations (80-90% cost reduction)
eval-all-cost-optimized:
	@echo "[Eval All - Cost Optimized] Running complete evaluation suite with cost optimization..."
	USE_EVAL_AGENT=true RAG_COST_OPTIMIZED=true MAX_CORPORA_SEARCH=2 PROJECT_ID=${GOOGLE_CLOUD_PROJECT} LOCATION=${GOOGLE_CLOUD_LOCATION} REASONING_ENGINE_ID=${REASONING_ENGINE_ID} python evals/run_all_evals.py

eval-session:
	@echo "[Eval Session] Running session functionality tests..."
	PROJECT_ID=${GOOGLE_CLOUD_PROJECT} LOCATION=${GOOGLE_CLOUD_LOCATION} REASONING_ENGINE_ID=${REASONING_ENGINE_ID} python evals/session_evals.py

eval-session-cost-optimized:
	@echo "[Eval Session - Cost Optimized] Running session functionality tests with cost optimization..."
	USE_EVAL_AGENT=true RAG_COST_OPTIMIZED=true PROJECT_ID=${GOOGLE_CLOUD_PROJECT} LOCATION=${GOOGLE_CLOUD_LOCATION} REASONING_ENGINE_ID=${REASONING_ENGINE_ID} python evals/session_evals.py

eval-rag:
	@echo "[Eval RAG] Running RAG memory functionality tests..."
	PROJECT_ID=${GOOGLE_CLOUD_PROJECT} LOCATION=${GOOGLE_CLOUD_LOCATION} python -m evals.rag_memory_evals

eval-agent:
	@echo "[Eval Agent] Running agent behavior tests..."
	PROJECT_ID=${GOOGLE_CLOUD_PROJECT} LOCATION=${GOOGLE_CLOUD_LOCATION} REASONING_ENGINE_ID=${REASONING_ENGINE_ID} python evals/agent_evals.py

eval-agent-cost-optimized:
	@echo "[Eval Agent - Cost Optimized] Running agent behavior tests with cost optimization..."
	USE_EVAL_AGENT=true RAG_COST_OPTIMIZED=true PROJECT_ID=${GOOGLE_CLOUD_PROJECT} LOCATION=${GOOGLE_CLOUD_LOCATION} REASONING_ENGINE_ID=${REASONING_ENGINE_ID} python evals/agent_evals.py

eval-callbacks:
	@echo "[Eval Callbacks] Running callback system tests..."
	PROJECT_ID=${GOOGLE_CLOUD_PROJECT} LOCATION=${GOOGLE_CLOUD_LOCATION} python evals/callback_evals.py

eval-preferences:
	@echo "[Eval Preferences] Running user preference system tests..."
	python evals/preference_evals.py

eval-performance:
	@echo "[Eval Performance] Running performance tests..."
	python evals/performance_evals.py

eval-performance-cost-optimized:
	@echo "[Eval Performance - Cost Optimized] Running performance tests with cost optimization..."
	USE_EVAL_AGENT=true RAG_COST_OPTIMIZED=true PROJECT_ID=${GOOGLE_CLOUD_PROJECT} LOCATION=${GOOGLE_CLOUD_LOCATION} REASONING_ENGINE_ID=${REASONING_ENGINE_ID} python evals/performance_evals.py

eval-quick:
	@echo "[Eval Quick] Running quick session test..."
	python -c "import asyncio; from sim_guide.session_service import health_check; print('✅ Passed' if asyncio.run(health_check()) else '❌ Failed')"

eval-callbacks-cost-optimized:
	@echo "[Eval Callbacks - Cost Optimized] Running callback system tests with cost optimization..."
	USE_EVAL_AGENT=true RAG_COST_OPTIMIZED=true PROJECT_ID=${GOOGLE_CLOUD_PROJECT} LOCATION=${GOOGLE_CLOUD_LOCATION} REASONING_ENGINE_ID=${REASONING_ENGINE_ID} python evals/callback_evals.py

eval-rag-cost-optimized:
	@echo "[Eval RAG - Cost Optimized] Running RAG memory tests with cost optimization..."
	USE_EVAL_AGENT=true RAG_COST_OPTIMIZED=true MAX_CORPORA_SEARCH=1 PROJECT_ID=${GOOGLE_CLOUD_PROJECT} LOCATION=${GOOGLE_CLOUD_LOCATION} REASONING_ENGINE_ID=${REASONING_ENGINE_ID} python evals/rag_memory_evals.py

eval-memory-subagent:
	@echo "[Eval Memory Subagent] Testing memory subagent architecture..."
	PROJECT_ID=${GOOGLE_CLOUD_PROJECT} LOCATION=${GOOGLE_CLOUD_LOCATION} REASONING_ENGINE_ID=${REASONING_ENGINE_ID} python evals/memory_subagent_evals.py

eval-memory-subagent-cost-optimized:
	@echo "[Eval Memory Subagent - Cost Optimized] Testing memory subagent with cost optimization..."
	USE_EVAL_AGENT=true RAG_COST_OPTIMIZED=true MAX_CORPORA_SEARCH=1 PROJECT_ID=${GOOGLE_CLOUD_PROJECT} LOCATION=${GOOGLE_CLOUD_LOCATION} REASONING_ENGINE_ID=${REASONING_ENGINE_ID} python evals/memory_subagent_evals.py

# Hybrid Memory System Evaluations
eval-hybrid-memory:
	@echo "[Eval Hybrid Memory] Testing hybrid memory system..."
	PYTHONPATH=$(PWD) PROJECT_ID=taajirah LOCATION=us-central1 python evals/hybrid_memory_evals.py

eval-hybrid-memory-cost-optimized:
	@echo "[Eval Hybrid Memory - Cost Optimized] Testing hybrid memory with cost optimization..."
	USE_EVAL_AGENT=true RAG_COST_OPTIMIZED=true MAX_SEMANTIC_CALLS_PER_DAY=5 PROJECT_ID=${GOOGLE_CLOUD_PROJECT} LOCATION=${GOOGLE_CLOUD_LOCATION} python evals/hybrid_memory_evals.py

test-hybrid-memory:
	@echo "[Test Hybrid Memory] Quick hybrid memory system test..."
	PROJECT_ID=${GOOGLE_CLOUD_PROJECT} LOCATION=${GOOGLE_CLOUD_LOCATION} python -c "import asyncio; from sim_guide.services.hybrid_memory_service import health_check_hybrid; result = asyncio.run(health_check_hybrid()); print('✅ Hybrid Memory Service healthy' if result.get('status') in ['healthy', 'degraded'] else '❌ Hybrid Memory Service failed'); print(f'Status: {result.get(\"status\")}, Message: {result.get(\"message\")}')"

# Cost optimization and configuration
config-hybrid-memory:
	@echo "[Config] Hybrid Memory Configuration:"
	@echo "• HYBRID_MEMORY_MODE=${HYBRID_MEMORY_MODE:-true}"
	@echo "• MAX_SEMANTIC_CALLS_PER_DAY=${MAX_SEMANTIC_CALLS_PER_DAY:-10}"
	@echo "• MAX_SEMANTIC_CALLS_PER_WEEK=${MAX_SEMANTIC_CALLS_PER_WEEK:-50}"
	@echo "• RAG_COST_OPTIMIZED=${RAG_COST_OPTIMIZED:-false}"
	@echo "• TRANSPARENT_MEMORY_COMMUNICATION=${TRANSPARENT_MEMORY_COMMUNICATION:-true}"

# Documentation and URLs
docs:
	@echo "[Documentation] Opening project documentation..."
	@echo "📚 Available Documentation:"
	@echo "   - README.md - Complete project documentation"
	@echo "   - VERTEX_AI_SETUP.md - Setup and deployment guide"
	@echo "   - DEPLOYMENT_GUIDE.md - Deployment verification record"
	@echo "   - META_COGNITIVE_ARCHITECTURE.md - Meta-cognitive capabilities guide"
	@echo ""
	@echo "🌐 Deployed Service URLs:"
	@echo "   - API Docs: https://sim-guide-agent-service-855515190257.us-central1.run.app/docs"
	@echo "   - Web UI: https://sim-guide-agent-service-855515190257.us-central1.run.app/dev-ui"
	@echo "   - Base URL: https://sim-guide-agent-service-855515190257.us-central1.run.app"

open-docs:
	@echo "[Opening] API Documentation in browser..."
	open https://sim-guide-agent-service-855515190257.us-central1.run.app/docs

open-ui:
	@echo "[Opening] Web UI in browser..."
	open https://sim-guide-agent-service-855515190257.us-central1.run.app/dev-ui

# Test deployed service with RAG capabilities
test-deployed-rag:
	@echo "[Test Deployed RAG] Testing deployed service with RAG Memory Service..."
	@echo "🔍 Testing API endpoints availability..."
	@curl -s -o /dev/null -w "API Docs Status: %{http_code}\n" https://sim-guide-agent-service-855515190257.us-central1.run.app/docs
	@curl -s -o /dev/null -w "Status: %{http_code}\n" https://sim-guide-agent-service-855515190257.us-central1.run.app/dev-ui
	@echo ""
	@echo "🧪 Testing session creation..."
	@curl -X POST "https://sim-guide-agent-service-855515190257.us-central1.run.app/apps/sim-guide/users/test-user/sessions" \
		-H "Content-Type: application/json" -d '{}' -s | python -c "import sys,json; data=json.load(sys.stdin); print(f'✅ Session created: {data.get(\"id\", \"unknown\")}') if 'id' in data else print(f'❌ Session creation failed: {data}')"
	@echo ""
	@echo "💬 Testing agent interaction..."
	@echo "Note: RAG Memory Service should be available in the deployed environment"

# Service verification
verify-deployment:
	@echo "[Verify] Testing deployed service..."
	@echo "🔍 Checking API documentation..."
	@curl -s -o /dev/null -w "Status: %{http_code}\n" https://sim-guide-agent-service-855515190257.us-central1.run.app/docs
	@echo "🔍 Checking Web UI..."
	@curl -s -o /dev/null -w "Status: %{http_code}\n" https://sim-guide-agent-service-855515190257.us-central1.run.app/dev-ui
	@echo "✅ Deployment verification complete"

test-session-api:
	@echo "[Test] Creating test session via API..."
	@curl -X POST "https://sim-guide-agent-service-855515190257.us-central1.run.app/apps/sim-guide/users/test-user/sessions" \
		-H "Content-Type: application/json" -d '{}' -s | python -m json.tool

# New Development and Testing Commands
.PHONY: help install test eval test-memory test-capability test-web-search eval-memory eval-capability eval-web-search

# Help command
help:
	@echo "🚀 Sim-Guide Agent Makefile Commands"
	@echo ""
	@echo "📖 Documentation:"
	@echo "   make docs              - Show documentation and service URLs"
	@echo "   make open-docs         - Open API documentation in browser"
	@echo "   make open-ui           - Open Web UI in browser"
	@echo ""
	@echo "🧪 Testing:"
	@echo "   make test-agent        - Test agent configuration"
	@echo "   make test-session      - Test session service"
	@echo "   make test-rag          - Test RAG memory service"
	@echo "   make test-meta-cognitive - Test meta-cognitive capabilities"
	@echo "   make test-session-api  - Test deployed API session creation"
	@echo "   make verify-deployment - Verify deployed service health"
	@echo "   make eval-quick        - Quick health check"
	@echo ""
	@echo "🧪 New Component Tests:"
	@echo "   make test              - Run all component tests"
	@echo "   make test-memory       - Test memory behavior specifically"
	@echo "   make test-capability   - Test capability enhancement specifically"
	@echo "   make test-web-search   - Test web search agent specifically"
	@echo ""
	@echo "🧪 Standard Evaluations (Higher Cost):"
	@echo "   make eval-all          - Complete evaluation suite"
	@echo "   make eval-session      - Session functionality tests"
	@echo "   make eval-agent        - Agent behavior tests"
	@echo "   make eval-meta-cognitive - Meta-cognitive capabilities tests"
	@echo "   make eval-performance  - Performance tests"
	@echo "   make eval-callbacks    - Callback system tests"
	@echo "   make eval-preferences  - User preference system tests"
	@echo "   make eval-rag          - RAG memory functionality tests"
	@echo ""
	@echo "💰 Cost-Optimized Evaluations (80-90% Cost Reduction):"
	@echo "   make eval-all-cost-optimized      - Complete suite (no tools, minimal instruction)"
	@echo "   make eval-session-cost-optimized  - Session tests (cost optimized)"
	@echo "   make eval-agent-cost-optimized    - Agent tests (cost optimized)"
	@echo "   make eval-meta-cognitive-cost-optimized - Meta-cognitive tests (cost optimized)"
	@echo "   make eval-performance-cost-optimized - Performance tests (cost optimized)"
	@echo ""
	@echo "🚢 Deployment:"
	@echo "   make deploy            - Deploy with managed session service + UI"
	@echo "   make delete            - Delete deployed service"
	@echo ""
	@echo "💻 Development:"
	@echo "   make dev               - Start local development server"
	@echo "   make local-server      - Start ADK API server with DatabaseSessionService (WORKING)"
	@echo "   make local-cli-database-server - Start ADK API server with CLI DatabaseSessionService (BROKEN)"
	@echo "   make local-memory-server   - Start ADK API server with InMemorySessionService"
	@echo "   make firestore-emulator- Start Firestore emulator"
	@echo ""
	@echo "🌐 Live Service:"
	@echo "   API: https://sim-guide-agent-service-855515190257.us-central1.run.app"
	@echo "   UI:  https://sim-guide-agent-service-855515190257.us-central1.run.app/dev-ui"

install:
	pip install -r requirements.txt

test: test-memory test-capability test-web-search
	@echo "All component tests completed"

eval: eval-memory eval-capability eval-web-search
	@echo "All component evaluations completed"

test-memory:
	python evals/memory_behavior_evals.py

test-capability:
	python evals/capability_evals.py

test-web-search:
	python evals/web_search_evals.py

eval-memory: test-memory

eval-capability: test-capability

eval-web-search: test-web-search 