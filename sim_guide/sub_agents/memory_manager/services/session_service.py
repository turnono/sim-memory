"""
Session Service Layer
Centralized session management for sim-memory application.
Provides business logic and clean abstractions over VertexAI session service.
"""

import logging
import os
import vertexai
from google.adk.sessions import VertexAiSessionService
from google.adk.runners import Runner

# Load .env file explicitly for Cloud Run compatibility
try:
    from dotenv import load_dotenv
    # Try loading from current directory first, then parent
    if os.path.exists('.env'):
        load_dotenv('.env')
    elif os.path.exists('../.env'):
        load_dotenv('../.env')
    elif os.path.exists('sim_guide/.env'):
        load_dotenv('sim_guide/.env')
except ImportError:
    # dotenv not available, environment should be set by Cloud Run
    pass

# Set up logging
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
APP_NAME = os.getenv("APP_NAME")
# Add flag to use cost-optimized agent for evaluations
USE_EVAL_AGENT = os.getenv("USE_EVAL_AGENT", "false").lower() == "true"


# Set up environment and Google Cloud credentials
if not os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
    # Only set for local development - Cloud Run handles credentials automatically
    local_service_account = "./taajirah-agents-service-account.json"
    if os.path.exists(local_service_account):
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = local_service_account


# Global instances - initialized lazily to avoid circular imports
_vertex_session_service = None
_runner = None
_current_agent_type = None  # Track which agent type is currently loaded


def get_root_agent():
    """Get root agent with lazy import to avoid circular dependencies"""
    if USE_EVAL_AGENT:
        from sim_guide.agent import eval_agent

        return eval_agent
    else:
        from sim_guide.agent import root_agent

        return root_agent



# Initialize Vertex AI lazily
def _get_vertex_session_service():
    """Get Vertex AI session service with lazy initialization"""
    global _vertex_session_service
    if _vertex_session_service is None:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        _vertex_session_service = VertexAiSessionService()
    return _vertex_session_service


# Initialize runner lazily
def _get_runner():
    """Get runner with lazy initialization"""
    global _runner, _current_agent_type

    # Check if we need to recreate the runner due to agent type change
    current_env_setting = os.getenv("USE_EVAL_AGENT", "false").lower() == "true"

    if _runner is None or _current_agent_type != current_env_setting:
        session_service = (
            _get_vertex_session_service()
        )  # Ensure vertex AI is initialized
        _runner = Runner(
            app_name=APP_NAME,
            agent=get_root_agent(),
            session_service=session_service,
        )
        _current_agent_type = current_env_setting
        logger.info(
            f"Runner initialized with agent type: {'eval' if current_env_setting else 'production'}"
        )

    return _runner


logger.info(f"Session service initialized for project {PROJECT_ID}")