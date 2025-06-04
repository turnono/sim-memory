"""
User Context Manager Services Module

Contains business logic services that handle user preference management,
session management, RAG memory, and other user context related logic.
"""

from .user_service import (
    UserPreferenceDetector,
    get_user_preferences,
    update_user_preferences,
    analyze_user_message_for_preferences,
    format_preferences_summary,
    get_personalized_instruction_context,
)

# Export user models
from .user_models import (
    UserPreferences,
    LifeExperienceLevel,
    CommunicationStyle,
    LifeArea,
)

# Export RAG memory service functions
from . import rag_memory_service

# Export session service functions
from . import session_service

__all__ = [
    # User preference management functions
    "get_user_preferences",
    "update_user_preferences",
    "analyze_user_message_for_preferences",
    "format_preferences_summary",
    "get_personalized_instruction_context",
    # User models and enums
    "UserPreferences",
    "LifeExperienceLevel",
    "CommunicationStyle",
    "LifeArea",
    # Service modules
    "rag_memory_service",
    "session_service",
]
