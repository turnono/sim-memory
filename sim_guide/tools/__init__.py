"""
Life Guidance Tools Module

This module registers function-based tools for the life guidance agent
following Google ADK best practices using FunctionTool.

Note: Memory and session tools are now handled by the specialized memory_session_manager subagent.
"""

from google.adk.tools import FunctionTool

# Import preference tools only (memory and session tools moved to subagent)
from .preferences import (
    get_user_preferences,
    set_user_preference,
    analyze_message_for_preferences,
    get_personalization_context,
)

# Create FunctionTool instances for preference tools
preference_tools = [
    FunctionTool(func=get_user_preferences),
    FunctionTool(func=set_user_preference),
    FunctionTool(func=analyze_message_for_preferences),
    FunctionTool(func=get_personalization_context),
]

# Only preference tools are exported (memory and session tools moved to subagent)
ALL_TOOLS = preference_tools

# Export for easy import
__all__ = ["ALL_TOOLS", "preference_tools"]
