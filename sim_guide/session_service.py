"""
Session Service Layer
Centralized session management for sim-memory application.
Provides business logic and clean abstractions over VertexAI session service.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import vertexai
from google.adk.sessions import VertexAiSessionService
from google.adk.runners import Runner
from google.genai import types
from sim_guide.agent import root_agent

# Set up logging
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")
REASONING_ENGINE_ID = os.getenv("REASONING_ENGINE_ID")

if not all([PROJECT_ID, LOCATION, REASONING_ENGINE_ID]):
    raise ValueError("PROJECT_ID, LOCATION, and REASONING_ENGINE_ID must be set")

# Clean up any quotes from environment variables
REASONING_ENGINE_ID = REASONING_ENGINE_ID.strip('"\'')

# Set up service account authentication
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./taajirah-agents-service-account.json")

# Initialize Vertex AI
vertexai.init(project=PROJECT_ID, location=LOCATION)

# Global instances - initialized once
_vertex_session_service = VertexAiSessionService(
    project=PROJECT_ID,
    location=LOCATION
)

_runner = Runner(
    agent=root_agent,
    app_name=REASONING_ENGINE_ID,
    session_service=_vertex_session_service
)

logger.info(f"Session service initialized for project {PROJECT_ID}")

async def create_session(
    user_id: str, 
    session_context: Optional[Dict[str, Any]] = None,
    session_type: str = "simulation_guide"
) -> Dict[str, Any]:
    """
    Create a new session with business logic and validation.
    
    Args:
        user_id: Unique identifier for the user
        session_context: Optional context data for the session
        session_type: Type of session (simulation_guide, admin, etc.)
        
    Returns:
        Dict containing session info
    """
    try:
        # Validate input
        if not user_id or not isinstance(user_id, str):
            raise ValueError("user_id must be a non-empty string")
        
        # Prepare session state with business logic
        session_state = {
            "session_type": session_type,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "user_id": user_id,
            "conversation_count": 0,
            "last_activity": datetime.now(timezone.utc).isoformat(),
            **(session_context or {})
        }
        
        # Create session via VertexAI
        session = await _vertex_session_service.create_session(
            app_name=REASONING_ENGINE_ID,
            user_id=user_id,
            state=session_state
        )
        
        session_info = {
            "session_id": session.id,
            "user_id": user_id,
            "session_type": session_type,
            "created_at": session_state["created_at"],
            "state": session_state
        }
        
        logger.info(f"Created session {session.id} for user {user_id} (type: {session_type})")
        return session_info
        
    except Exception as e:
        logger.error(f"Failed to create session for user {user_id}: {e}")
        raise

async def get_session(user_id: str, session_id: str) -> Dict[str, Any]:
    """
    Retrieve session information with business logic.
    
    Args:
        user_id: User identifier
        session_id: Session identifier
        
    Returns:
        Dict containing session information
    """
    try:
        session = await _vertex_session_service.get_session(
            app_name=REASONING_ENGINE_ID,
            user_id=user_id,
            session_id=session_id
        )
        
        return {
            "session_id": session.id,
            "user_id": session.user_id,
            "app_name": session.app_name,
            "state": session.state,
            "last_update_time": session.last_update_time,
            "created_at": session.state.get("created_at"),
            "session_type": session.state.get("session_type", "unknown"),
            "conversation_count": session.state.get("conversation_count", 0)
        }
        
    except Exception as e:
        logger.error(f"Failed to get session {session_id} for user {user_id}: {e}")
        raise

async def send_message(
    user_id: str, 
    session_id: str, 
    message: str,
    message_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Send a message to the agent with session management.
    
    Args:
        user_id: User identifier
        session_id: Session identifier  
        message: User message
        message_metadata: Optional metadata about the message
        
    Returns:
        Dict containing response and metadata
    """
    try:
        # Prepare message content
        content = types.Content(role='user', parts=[types.Part(text=message)])
        
        # Send via runner
        final_response = None
        start_time = datetime.now(timezone.utc)
        
        async for event in _runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content
        ):
            if event.is_final_response() and event.content and event.content.parts:
                final_response = event.content.parts[0].text
                break
        
        end_time = datetime.now(timezone.utc)
        response_time = (end_time - start_time).total_seconds()
        
        result = {
            "session_id": session_id,
            "user_message": message,
            "agent_response": final_response or "No response received",
            "status": "success" if final_response else "no_response",
            "response_time_seconds": response_time,
            "timestamp": end_time.isoformat(),
            "metadata": message_metadata or {}
        }
        
        logger.debug(f"Message processed for session {session_id}: {len(message)} chars -> {len(result['agent_response'])} chars")
        return result
        
    except Exception as e:
        logger.error(f"Failed to send message in session {session_id}: {e}")
        return {
            "session_id": session_id,
            "user_message": message,
            "agent_response": f"Error: {str(e)}",
            "status": "error",
            "response_time_seconds": 0,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": message_metadata or {}
        }

async def list_user_sessions(
    user_id: str,
    session_type: Optional[str] = None
) -> List[str]:
    """
    List all sessions for a user.
    
    Args:
        user_id: User identifier
        session_type: Optional filter by session type
        
    Returns:
        List of session IDs
    """
    try:
        sessions_response = await _vertex_session_service.list_sessions(
            app_name=REASONING_ENGINE_ID,
            user_id=user_id
        )
        
        # Handle different response formats
        if hasattr(sessions_response, 'session_ids'):
            session_ids = sessions_response.session_ids
        elif hasattr(sessions_response, 'sessions'):
            session_ids = [session.id for session in sessions_response.sessions]
        else:
            logger.warning(f"Unexpected sessions response format: {sessions_response}")
            session_ids = []
        
        # Filter by session type if specified
        if session_type:
            filtered_sessions = []
            for session_id in session_ids:
                try:
                    session_info = await get_session(user_id, session_id)
                    if session_info.get("session_type") == session_type:
                        filtered_sessions.append(session_id)
                except Exception as e:
                    logger.warning(f"Could not check session {session_id} type: {e}")
            session_ids = filtered_sessions
        
        logger.debug(f"Found {len(session_ids)} sessions for user {user_id}")
        return session_ids
        
    except Exception as e:
        logger.error(f"Failed to list sessions for user {user_id}: {e}")
        return []

async def delete_session(user_id: str, session_id: str) -> bool:
    """
    Delete a session with logging.
    
    Args:
        user_id: User identifier
        session_id: Session identifier
        
    Returns:
        True if successful
    """
    try:
        await _vertex_session_service.delete_session(
            app_name=REASONING_ENGINE_ID,
            user_id=user_id,
            session_id=session_id
        )
        
        logger.info(f"Deleted session {session_id} for user {user_id}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to delete session {session_id}: {e}")
        return False

async def health_check() -> Dict[str, Any]:
    """
    Perform health check on the session service.
    
    Returns:
        Dict containing health status
    """
    try:
        start_time = datetime.now(timezone.utc)
        
        # Test session creation
        test_user = "health_check_user"
        session_info = await create_session(
            user_id=test_user,
            session_context={"health_check": True},
            session_type="health_check"
        )
        
        # Test messaging
        response = await send_message(
            user_id=test_user,
            session_id=session_info["session_id"],
            message="Health check message"
        )
        
        # Test cleanup
        await delete_session(test_user, session_info["session_id"])
        
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        success = (
            response["status"] == "success" and
            len(response["agent_response"]) > 0
        )
        
        return {
            "status": "healthy" if success else "degraded",
            "duration_seconds": duration,
            "timestamp": end_time.isoformat(),
            "test_response_received": success,
            "project_id": PROJECT_ID,
            "location": LOCATION,
            "reasoning_engine_id": REASONING_ENGINE_ID
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        } 