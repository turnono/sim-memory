"""
User Context Manager Tools Module

Contains all tools used by the user context manager agent for memory operations,
session management, and user preferences.
"""

from .memory import (
    load_life_guidance_memory,
    preload_life_context,
    load_life_resources,
)

from .session import (
    analyze_session_context,
    get_conversation_continuity_hints,
    update_session_context,
)

from .preferences import (
    get_user_preferences,
    set_user_preference,
    analyze_message_for_preferences,
    get_personalization_context,
)

__all__ = [
    # Memory tools
    "load_life_guidance_memory",
    "preload_life_context",
    "load_life_resources",
    # Session tools
    "analyze_session_context",
    "get_conversation_continuity_hints",
    "update_session_context",
    # Preference tools
    "get_user_preferences",
    "set_user_preference",
    "analyze_message_for_preferences",
    "get_personalization_context",
] 