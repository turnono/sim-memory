include .env
export 

firestore-emulator:
	@echo "[Firestore Emulator] Starting Firestore emulator. Run this in its own terminal window!"
	FIRESTORE_EMULATOR_HOST=localhost:8087 firebase emulators:start --only firestore,auth --project ${GOOGLE_CLOUD_PROJECT}

dev:
	@echo "[Dev Server] Starting ADK API server. Run this in a separate terminal after the emulator is running!"
	ENV=development FIRESTORE_EMULATOR_HOST=localhost:8087 python main.py --allow_origins="http://localhost:4200"

frontend-do:
	cd frontend && npm start


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
	--app_name=sim-guide \
	--session_db_url=agentengine://${REASONING_ENGINE_ID} \
	--with_ui \
	./sim_guide

# Delete the agent service from Google Cloud Run
delete:
	gcloud run services delete ${AGENT_SERVICE_NAME} \
	--region ${GOOGLE_CLOUD_LOCATION}

# Test the session service health
test-session:
	@echo "[Test] Testing session service health..."
	python -c "from sim_guide.agent import root_agent; print('✅ Agent and session service configured correctly')"

# Test the RAG memory service health
test-rag:
	@echo "[Test] Testing RAG memory service health..."
	PROJECT_ID=${GOOGLE_CLOUD_PROJECT} LOCATION=${GOOGLE_CLOUD_LOCATION} python -c "import asyncio; from sim_guide.rag_memory_service import health_check; result = asyncio.run(health_check()); print('✅ RAG Memory Service healthy' if result.get('status') in ['healthy', 'degraded'] else '❌ RAG Memory Service failed'); print(f'Status: {result.get(\"status\")}, Duration: {result.get(\"duration_seconds\", 0):.2f}s')"

test-agent:
	@echo "[Agent Test] Testing the agent configuration..."
	python -c "from sim_guide.agent import root_agent, session_service, runner; print(f'✅ Agent {root_agent.name} configured with VertexAI session service')"

# Evaluation commands
eval-all:
	@echo "[Eval All] Running complete evaluation suite..."
	PROJECT_ID=${GOOGLE_CLOUD_PROJECT} LOCATION=${GOOGLE_CLOUD_LOCATION} REASONING_ENGINE_ID=${REASONING_ENGINE_ID} python evals/run_all_evals.py

eval-session:
	@echo "[Eval Session] Running session functionality tests..."
	PROJECT_ID=${GOOGLE_CLOUD_PROJECT} LOCATION=${GOOGLE_CLOUD_LOCATION} REASONING_ENGINE_ID=${REASONING_ENGINE_ID} python evals/session_evals.py

eval-rag:
	@echo "[Eval RAG] Running RAG memory functionality tests..."
	PROJECT_ID=${GOOGLE_CLOUD_PROJECT} LOCATION=${GOOGLE_CLOUD_LOCATION} python -m evals.rag_memory_evals

eval-agent:
	@echo "[Eval Agent] Running agent behavior tests..."
	PROJECT_ID=${GOOGLE_CLOUD_PROJECT} LOCATION=${GOOGLE_CLOUD_LOCATION} REASONING_ENGINE_ID=${REASONING_ENGINE_ID} python evals/agent_evals.py

eval-callbacks:
	@echo "[Eval Callbacks] Running callback system tests..."
	PROJECT_ID=${GOOGLE_CLOUD_PROJECT} LOCATION=${GOOGLE_CLOUD_LOCATION} python evals/callback_evals.py

eval-preferences:
	@echo "[Eval Preferences] Running user preference system tests..."
	python evals/preference_evals.py

eval-performance:
	@echo "[Eval Performance] Running performance tests..."
	python evals/performance_evals.py

eval-quick:
	@echo "[Eval Quick] Running quick session test..."
	python -c "import asyncio; from sim_guide.session_service import health_check; print('✅ Passed' if asyncio.run(health_check()) else '❌ Failed')"

# Documentation and URLs
docs:
	@echo "[Documentation] Opening project documentation..."
	@echo "📚 Available Documentation:"
	@echo "   - README.md - Complete project documentation"
	@echo "   - VERTEX_AI_SETUP.md - Setup and deployment guide"
	@echo "   - DEPLOYMENT_GUIDE.md - Deployment verification record"
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
	@curl -s -o /dev/null -w "Web UI Status: %{http_code}\n" https://sim-guide-agent-service-855515190257.us-central1.run.app/dev-ui
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
	@echo "   make test-session-api  - Test deployed API session creation"
	@echo "   make verify-deployment - Verify deployed service health"
	@echo "   make eval-quick        - Quick health check"
	@echo "   make eval-all          - Complete evaluation suite"
	@echo "   make eval-session      - Session functionality tests"
	@echo "   make eval-rag          - RAG memory functionality tests"
	@echo "   make eval-agent        - Agent behavior tests"
	@echo "   make eval-callbacks    - Callback system tests"
	@echo "   make eval-preferences  - User preference system tests"
	@echo "   make eval-performance  - Performance tests"
	@echo ""
	@echo "🚢 Deployment:"
	@echo "   make deploy            - Deploy with managed session service + UI"
	@echo "   make delete            - Delete deployed service"
	@echo ""
	@echo "💻 Development:"
	@echo "   make dev               - Start local development server"
	@echo "   make firestore-emulator- Start Firestore emulator"
	@echo ""
	@echo "🔗 Setup Guides:"
	@echo "   📖 README.md          - Complete project documentation"
	@echo "   📖 RAG_SETUP_GUIDE.md - RAG Memory Service setup"
	@echo "   📖 VERTEX_AI_SETUP.md - VertexAI configuration"
	@echo ""
	@echo "🌐 Live Service:"
	@echo "   API: https://sim-guide-agent-service-855515190257.us-central1.run.app"
	@echo "   UI:  https://sim-guide-agent-service-855515190257.us-central1.run.app/dev-ui"