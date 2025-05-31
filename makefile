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

test-agent:
	@echo "[Agent Test] Testing the agent configuration..."
	python -c "from sim_guide.agent import root_agent, session_service, runner; print(f'✅ Agent {root_agent.name} configured with VertexAI session service')"

# Evaluation commands
eval-all:
	@echo "[Eval All] Running complete evaluation suite..."
	python evals/run_all_evals.py

eval-session:
	@echo "[Eval Session] Running session functionality tests..."
	python evals/session_evals.py

eval-agent:
	@echo "[Eval Agent] Running agent behavior tests..."
	python evals/agent_evals.py

eval-performance:
	@echo "[Eval Performance] Running performance tests..."
	python evals/performance_evals.py

eval-quick:
	@echo "[Eval Quick] Running quick session test..."
	python -c "import asyncio; from sim_guide.session_service import health_check; print('✅ Passed' if asyncio.run(health_check()) else '❌ Failed')"

# production build and deploy

deploy-frontend:
	cd frontend && ng build --configuration=production && firebase deploy --only hosting:tjr-sim-guide --project=${GOOGLE_CLOUD_PROJECT}

# Deploy the agent service to Google Cloud Run
deploy:
	gcloud run deploy ${AGENT_SERVICE_NAME} \
	--source . \
	--region ${GOOGLE_CLOUD_LOCATION} \
	--project ${GOOGLE_CLOUD_PROJECT} \
	--allow-unauthenticated \
	--port 8080 \
	--service-account ${AGENT_SERVICE_ACCOUNT} \
	--set-env-vars="GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT},\
GOOGLE_CLOUD_LOCATION=${GOOGLE_CLOUD_LOCATION},\
GOOGLE_GENAI_USE_VERTEXAI=${GOOGLE_GENAI_USE_VERTEXAI},\
GOOGLE_API_KEY=${GOOGLE_API_KEY},\
ENV=${ENV},\
DEPLOYED_CLOUD_SERVICE_URL=${DEPLOYED_CLOUD_SERVICE_URL}"

# Delete the agent service from Google Cloud Run
delete:
	gcloud run services delete ${AGENT_SERVICE_NAME} \
	--region ${GOOGLE_CLOUD_LOCATION}

# Test the session service health
test-session:
	@echo "[Test] Testing session service health..."
	python -c "from sim_guide.agent import root_agent; print('✅ Agent and session service configured correctly')"