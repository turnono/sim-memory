"""
Services Module for Life Guidance

Contains business logic services that handle data processing, user management,
session management, RAG memory, and other application logic following ADK best practices.
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

# Export RAG memory service functions (imported on demand)
from . import rag_memory_service
# Note: session_service not imported here to avoid circular dependency

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
    # session_service available via direct import
]
