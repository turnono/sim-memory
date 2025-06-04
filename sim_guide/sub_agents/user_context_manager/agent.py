"""
User Context Management Subagent

A specialized agent focused exclusively on user context management including:
memory operations, session management, user preferences, RAG integration,
and long-term context management for the life guidance system.

This agent handles:
- Loading and searching memories with ADK-aligned hybrid routing
- Managing RAG corpus operations
- Context preloading and optimization
- Memory storage and retrieval
- Cross-session memory continuity
- Session context analysis and management
- Conversation continuity tracking
- User preferences and personalization
- User profile management
"""

import logging
from google.adk import Agent
from google.adk.tools import FunctionTool

# Import prompts
from .prompt import DESCRIPTION, INSTRUCTION

# Import memory tools
from .tools import (
    load_life_guidance_memory,
    preload_life_context,
    load_life_resources,
    # Session tools
    analyze_session_context,
    get_conversation_continuity_hints,
    update_session_context,
    # Preference tools
    get_user_preferences,
    set_user_preference,
    analyze_message_for_preferences,
    get_personalization_context,
)

logger = logging.getLogger(__name__)


# === MEMORY AGENT CONFIGURATION ===

# Memory management tools using the moved memory tools
memory_tools = [
    FunctionTool(func=load_life_guidance_memory),
    FunctionTool(func=preload_life_context),
    FunctionTool(func=load_life_resources),
]

# Session management tools using the moved session tools
session_tools = [
    FunctionTool(func=analyze_session_context),
    FunctionTool(func=get_conversation_continuity_hints),
    FunctionTool(func=update_session_context),
]

# User preference tools (now moved from root)
preference_tools = [
    FunctionTool(func=get_user_preferences),
    FunctionTool(func=set_user_preference),
    FunctionTool(func=analyze_message_for_preferences),
    FunctionTool(func=get_personalization_context),
]

# Combine all user context management tools
all_user_context_tools = memory_tools + session_tools + preference_tools

# Memory Management Agent
user_context_manager = Agent(
    name="user_context_manager",
    model="gemini-2.0-flash",
    description=DESCRIPTION,
    instruction=INSTRUCTION,
    output_key="memory_search_result",  # String key for memory operations
    tools=all_user_context_tools,
)


def get_user_context_manager():
    """
    Returns the user context manager agent for use by the root agent.

    Returns:
        Agent: The configured user context manager with memory and session capabilities
    """
    return user_context_manager


# Export for use in main agent
__all__ = ["user_context_manager", "get_user_context_manager"]
