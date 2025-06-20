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

        # Check for loaded resources
        loaded_resources = tool_context.state.get("temp:loaded_resources", [])
        if loaded_resources:
            context_info.append(f"Resources available: {', '.join(loaded_resources[:3])}")

        # Check for specific context items we know about
        session_items = 0
        if tool_context.state.get("temp:conversation_summary"):
            session_items += 1
        if tool_context.state.get("temp:user_context"):
            session_items += 1
        if tool_context.state.get("temp:topic_focus"):
            session_items += 1
        
        if session_items > 0:
            context_info.append(f"Session context available: {session_items} items")

        # Check for preloaded contexts (check specific known keys)
        preloaded_contexts = []
        if tool_context.state.get("temp:preloaded_guidance"):
            preloaded_contexts.append("guidance")
        if tool_context.state.get("temp:preloaded_memory"):
            preloaded_contexts.append("memory")
        if tool_context.state.get("temp:preloaded_preferences"):
            preloaded_contexts.append("preferences")
        
        if preloaded_contexts:
            context_info.append(f"Preloaded contexts: {', '.join(preloaded_contexts[:2])}")

        analysis = "; ".join(context_info)

        return {
            "action": "analyze_session_context",
            "analysis": analysis,
            "user_identified": bool(user_name),
            "resources_loaded": len(loaded_resources),
            "contexts_preloaded": len(preloaded_contexts),
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

        # Check if user identification is missing
        has_name = tool_context.state.get("user:name")
        if not has_name:
            hints.append("Consider asking for user's name for personalization")

        # Check for stored user contexts (check specific known user keys)
        user_contexts = []
        if tool_context.state.get("user:preferences"):
            user_contexts.append("preferences")
        if tool_context.state.get("user:goals"):
            user_contexts.append("goals")
        if tool_context.state.get("user:context"):
            user_contexts.append("context")
        if tool_context.state.get("user:history"):
            user_contexts.append("history")
        
        # Check if this seems like a new conversation (based on available context)
        total_context_items = len(user_contexts)
        if tool_context.state.get("temp:conversation_summary"):
            total_context_items += 1
        if tool_context.state.get("current_topic"):
            total_context_items += 1
        
        is_new_conversation = total_context_items < 2
        
        if is_new_conversation:
            hints.append("New conversation - consider introduction and context gathering")

        if user_contexts:
            context_types = user_contexts[:3]
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
            "is_new_conversation": is_new_conversation,
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


def save_session_to_memory(context_summary: str, tool_context: ToolContext) -> dict:
    """Save current session context to long-term memory for future retrieval.
    
    This should be called at the end of meaningful conversations or when 
    important context needs to be preserved for future sessions.

    Args:
        context_summary: Summary of the key context/insights from this session
        tool_context: Context for accessing session info and memory service

    Returns:
        Dictionary with save operation result
    """
    logger.info("Saving session to long-term memory")

    try:
        # Note: The actual memory saving is handled by the Runner's memory service
        # through ADK's automatic session-to-memory integration
        
        # Mark this session as saved for memory
        tool_context.state["temp:session_saved_to_memory"] = True
        tool_context.state["temp:memory_summary"] = context_summary
        
        return {
            "action": "save_session_to_memory",
            "summary": context_summary,
            "message": f"Session context saved to memory: {context_summary[:100]}{'...' if len(context_summary) > 100 else ''}"
        }
        
    except Exception as e:
        logger.error(f"Error saving session to memory: {e}")
        return {
            "action": "save_session_to_memory", 
            "summary": context_summary,
            "message": f"Error saving session: {str(e)}"
        }
