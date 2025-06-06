"""
Memory Management Tools for Life Guidance

Simple memory tools following ADK patterns using tool_context and session state.
"""

import logging
from google.adk.tools.tool_context import ToolContext
from google.adk.tools import load_memory

logger = logging.getLogger(__name__)


def store_user_context(context_info: str, context_type: str, tool_context: ToolContext) -> dict:
    """Store user context information in session state.

    Args:
        context_info: The context information to store
        context_type: Type of context (personal, goal, preference, situation, etc.)
        tool_context: Context for accessing and updating session state

    Returns:
        A confirmation message
    """
    logger.info(f"Storing user context: {context_type}")

    # Store in session state with appropriate key
    context_key = f"user:{context_type}"
    tool_context.state[context_key] = context_info

    return {
        "action": "store_user_context",
        "context_type": context_type,
        "message": f"Stored {context_type} context: {context_info[:100]}{'...' if len(context_info) > 100 else ''}",
    }


def get_user_context(context_type: str, tool_context: ToolContext) -> dict:
    """Get stored user context information.

    Args:
        context_type: Type of context to retrieve (personal, goal, preference, situation, etc.)
        tool_context: Context for accessing session state

    Returns:
        The stored context information
    """
    logger.info(f"Retrieving user context: {context_type}")

    # Get from session state
    context_key = f"user:{context_type}"
    context_info = tool_context.state.get(context_key, "")

    return {
        "action": "get_user_context",
        "context_type": context_type,
        "context_info": context_info,
        "found": bool(context_info),
    }


def preload_life_context(context_type: str, tool_context: ToolContext) -> dict:
    """Preload relevant context for ongoing conversations.

    Args:
        context_type: Type of context to preload (general, career, relationships, health, finance, etc.)
        tool_context: Context for accessing session state and memory

    Returns:
        Dictionary with preloaded context information
    """
    logger.info(f"Preloading life context: {context_type}")

    try:
        # Get any stored context for this type
        stored_context = get_user_context(context_type, tool_context)
        
        # Also search memory for related conversations using ADK's load_memory
        memory_query = f"{context_type} guidance conversations goals challenges"
        try:
            memory_results = load_memory(memory_query, tool_context)
        except Exception as e:
            logger.warning(f"Memory search failed: {e}")
            memory_results = []
        
        # Store preloaded context marker
        tool_context.state[f"temp:preloaded_{context_type}"] = True
        
        return {
            "action": "preload_life_context",
            "context_type": context_type,
            "stored_context": stored_context.get("context_info", ""),
            "memory_results": memory_results if memory_results else [],
            "message": f"Preloaded {context_type} context - found {len(memory_results) if memory_results else 0} related memories"
        }
    except Exception as e:
        logger.error(f"Error preloading context: {e}")
        return {
            "action": "preload_life_context",
            "context_type": context_type,
            "stored_context": "",
            "memory_results": [],
            "message": f"Context preloading unavailable: {str(e)}"
        }


def load_life_resources(resource_type: str, tool_context: ToolContext) -> dict:
    """Load specific life guidance resources and artifacts.

    Args:
        resource_type: Type of resource to load (frameworks, templates, strategies, etc.)
        tool_context: Context for accessing stored resources

    Returns:
        Dictionary with resource information
    """
    logger.info(f"Loading life resources: {resource_type}")

    # Define available life guidance resources
    resources = {
        "goal_setting": [
            "SMART goals framework (Specific, Measurable, Achievable, Relevant, Time-bound)",
            "Goal decomposition strategy: Break large goals into smaller milestones",
            "Progress tracking templates for accountability"
        ],
        "decision_making": [
            "Pro/Con analysis framework with weighted criteria",
            "Future self visualization technique",
            "Decision reversal test: 'Will I regret not trying this?'"
        ],
        "stress_management": [
            "4-7-8 breathing technique for immediate calm",
            "Time blocking strategy for workload management", 
            "Perspective reframing: 'What would I tell a friend in this situation?'"
        ],
        "career": [
            "Skills gap analysis template",
            "Professional network mapping strategy",
            "Career pivot framework: transferable skills identification"
        ],
        "relationships": [
            "Active listening checklist",
            "Conflict resolution steps: pause, understand, respond",
            "Boundary setting scripts and frameworks"
        ],
        "health": [
            "Habit stacking technique for building routines",
            "Energy management: track patterns of high/low energy",
            "Minimum viable progress: small consistent actions"
        ],
        "finance": [
            "50/30/20 budgeting framework (needs/wants/savings)",
            "Emergency fund building strategy",
            "Investment basics: diversification and risk tolerance"
        ]
    }

    available_resources = resources.get(resource_type, [])
    
    # Store loaded resources marker
    if available_resources:
        current_loaded = tool_context.state.get("temp:loaded_resources", [])
        if resource_type not in current_loaded:
            current_loaded.append(resource_type)
            tool_context.state["temp:loaded_resources"] = current_loaded

    return {
        "action": "load_life_resources",
        "resource_type": resource_type,
        "resources": available_resources,
        "found": bool(available_resources),
        "message": f"Loaded {len(available_resources)} {resource_type} resources"
    }
