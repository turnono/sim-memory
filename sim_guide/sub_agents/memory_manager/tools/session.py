"""
Session Management Tools for Life Guidance

Simple session tools following ADK patterns using tool_context and session state.
"""

import logging
from google.adk.tools.tool_context import ToolContext

logger = logging.getLogger(__name__)


def analyze_session_context(tool_context: ToolContext) -> dict:
    """Analyze current session context to understand conversation state and user engagement.

    Args:
        tool_context: Context for accessing session state

    Returns:
        Dictionary with session analysis
    """
    logger.info("Analyzing session context")

    try:
        context_info = []

        # Check for user identification
        user_name = tool_context.state.get("user:name", "")
        if user_name:
            context_info.append(f"User: {user_name}")
        else:
            context_info.append("User: Not identified")

        # Check conversation history indicators
        temp_keys = [key for key in tool_context.state.keys() if key.startswith("temp:")]
        if temp_keys:
            context_info.append(f"Session context available: {len(temp_keys)} items")

        # Check for loaded resources
        loaded_resources = tool_context.state.get("temp:loaded_resources", [])
        if loaded_resources:
            context_info.append(f"Resources available: {', '.join(loaded_resources[:3])}")

        # Check for preloaded contexts
        preloaded_keys = [key for key in tool_context.state.keys() if key.startswith("temp:preloaded_")]
        if preloaded_keys:
            contexts = [key.replace("temp:preloaded_", "") for key in preloaded_keys]
            context_info.append(f"Preloaded contexts: {', '.join(contexts[:2])}")

        analysis = "; ".join(context_info)

        return {
            "action": "analyze_session_context",
            "analysis": analysis,
            "user_identified": bool(user_name),
            "resources_loaded": len(loaded_resources),
            "contexts_preloaded": len(preloaded_keys),
            "message": f"Session Analysis: {analysis}"
        }

    except Exception as e:
        logger.error(f"Error analyzing session context: {e}")
        return {
            "action": "analyze_session_context",
            "analysis": f"Error analyzing session: {str(e)}",
            "user_identified": False,
            "resources_loaded": 0,
            "contexts_preloaded": 0,
            "message": f"Error: Failed to analyze session context: {str(e)}"
        }


def get_conversation_continuity_hints(tool_context: ToolContext) -> dict:
    """Get hints for maintaining conversation continuity based on session state.

    Args:
        tool_context: Context for accessing session state

    Returns:
        Dictionary with continuity suggestions
    """
    logger.info("Getting conversation continuity hints")

    try:
        hints = []

        # Check if this seems like a new conversation
        session_keys = list(tool_context.state.keys())
        if not session_keys or len(session_keys) < 3:
            hints.append("New conversation - consider introduction and context gathering")

        # Check if user identification is missing
        has_name = tool_context.state.get("user:name")
        if not has_name:
            hints.append("Consider asking for user's name for personalization")

        # Check for stored user contexts
        user_contexts = [key for key in tool_context.state.keys() if key.startswith("user:")]
        if user_contexts:
            context_types = [key.replace("user:", "") for key in user_contexts[:3]]
            hints.append(f"Available context: {', '.join(context_types)}")

        # Check for loaded resources that could be referenced
        resources = tool_context.state.get("temp:loaded_resources", [])
        if resources:
            hints.append(f"Available resources to reference: {', '.join(resources[:2])}")

        if not hints:
            hints.append("Well-established session - maintain current conversation flow")

        return {
            "action": "get_conversation_continuity_hints",
            "hints": hints,
            "is_new_conversation": len(session_keys) < 3,
            "user_identified": bool(has_name),
            "available_contexts": len(user_contexts),
            "message": f"Continuity hints: {'; '.join(hints)}"
        }

    except Exception as e:
        logger.error(f"Error getting continuity hints: {e}")
        return {
            "action": "get_conversation_continuity_hints",
            "hints": [f"Error getting hints: {str(e)}"],
            "is_new_conversation": True,
            "user_identified": False,
            "available_contexts": 0,
            "message": f"Error: Failed to get continuity hints: {str(e)}"
        }


def update_session_context(context_type: str, context_value: str, tool_context: ToolContext) -> dict:
    """Update session context with new information for conversation continuity.

    Args:
        context_type: Type of context to store (topic, focus, mood, etc.)
        context_value: The context value to store
        tool_context: Context for accessing and updating session state

    Returns:
        Dictionary with update confirmation
    """
    logger.info(f"Updating session context: {context_type}")

    try:
        # Store context with temp: prefix for session-temporary data
        context_key = f"temp:context_{context_type}"
        tool_context.state[context_key] = context_value

        return {
            "action": "update_session_context",
            "context_type": context_type,
            "context_value": context_value,
            "context_key": context_key,
            "message": f"Updated session context: {context_type} = {context_value}"
        }

    except Exception as e:
        logger.error(f"Error updating session context: {e}")
        return {
            "action": "update_session_context",
            "context_type": context_type,
            "context_value": context_value,
            "context_key": None,
            "message": f"Error: Failed to update session context: {str(e)}"
        }
