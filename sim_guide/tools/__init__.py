"""
Life Guidance Tools Module

This module registers all function-based tools for the life guidance agent
following Google ADK best practices using FunctionTool.
"""

from google.adk.tools import FunctionTool

# Import all tool functions
from .memory import (
    load_life_guidance_memory,
    preload_life_context,
    load_life_resources
)

from .preferences import (
    get_user_preferences,
    set_user_preference,
    analyze_message_for_preferences,
    get_personalization_context
)

from .session import (
    analyze_session_context,
    get_conversation_continuity_hints,
    update_session_context
)

# Create FunctionTool instances for memory tools
memory_tools = [
    FunctionTool(func=load_life_guidance_memory),
    FunctionTool(func=preload_life_context),
    FunctionTool(func=load_life_resources)
]

# Create FunctionTool instances for preference tools
preference_tools = [
    FunctionTool(func=get_user_preferences),
    FunctionTool(func=set_user_preference),
    FunctionTool(func=analyze_message_for_preferences),
    FunctionTool(func=get_personalization_context)
]

# Create FunctionTool instances for session tools
session_tools = [
    FunctionTool(func=analyze_session_context),
    FunctionTool(func=get_conversation_continuity_hints),
    FunctionTool(func=update_session_context)
]

# Combine all tools
ALL_LIFE_GUIDANCE_TOOLS = memory_tools + preference_tools + session_tools

# Export for easy import
__all__ = [
    'ALL_LIFE_GUIDANCE_TOOLS',
    'memory_tools', 
    'preference_tools',
    'session_tools'
] 