"""
Memory Manager Tools Module

Contains tools for memory operations and session management following ADK patterns.
All tools use tool_context for session state management and follow ADK conventions.

Note: Memory search is handled by ADK's built-in load_memory tool.
"""

from .memory import (
    store_user_context,
    get_user_context,
    preload_life_context,
    load_life_resources,
)

from .session import (
    analyze_session_context,
    get_conversation_continuity_hints,
    update_session_context,
)

__all__ = [
    "store_user_context",
    "get_user_context",
    "preload_life_context",
    "load_life_resources",
    # Session tools
    "analyze_session_context",
    "get_conversation_continuity_hints",
    "update_session_context",
]
