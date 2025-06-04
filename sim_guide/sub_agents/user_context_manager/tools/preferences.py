"""
ADK Function Tools for Life Guidance User Preference Management

These functions allow the agent to get, set, and update user preferences
for daily life and long-term goal guidance.
"""

import logging
from typing import Dict, Any, Optional, List, Union
from google.adk.tools import ToolContext

# Import from the new organized modules
from ..services import (
    UserPreferences,
    LifeExperienceLevel,
    CommunicationStyle,
    LifeArea,
    get_user_preferences as service_get_user_preferences,
    update_user_preferences as service_update_user_preferences,
    format_preferences_summary,
    get_personalized_instruction_context,
    analyze_user_message_for_preferences as service_analyze_user_message_for_preferences,
)

logger = logging.getLogger(__name__)


def get_user_preferences(tool_context) -> str:
    """
    Get current user preferences for life guidance including name, life experience level,
    communication style, focus areas, and goals.

    Args:
        tool_context: ADK ToolContext providing access to session state

    Returns:
        str: Formatted summary of current user preferences.
    """
    try:
        # Get session state from ADK ToolContext
        session_state = getattr(tool_context, "state", {}) if tool_context else {}
        preferences = service_get_user_preferences(session_state)

        summary = format_preferences_summary(preferences)
        return summary

    except Exception as e:
        logger.error(f"Error getting user preferences: {e}")
        return f"Error: Failed to get user preferences: {str(e)}"


def set_user_preference(
    preference_name: str, preference_value: str, tool_context
) -> str:
    """
    Set a specific user life guidance preference.

    Args:
        preference_name: Name of the preference to set (e.g., 'name', 'life_experience_level', 'communication_style')
        preference_value: Value to set for the preference
        tool_context: ADK ToolContext providing access to session state

    Returns:
        str: Status message indicating success or failure.
    """
    try:
        # Get session state from ADK ToolContext
        session_state = getattr(tool_context, "state", {}) if tool_context else {}
        preferences = service_get_user_preferences(session_state)

        # Handle different preference types for life guidance
        if preference_name == "name" or preference_name == "user_name":
            preferences.user_name = preference_value

        elif (
            preference_name == "life_experience_level"
            or preference_name == "experience_level"
        ):
            try:
                preferences.life_experience_level = LifeExperienceLevel(
                    preference_value.lower()
                )
            except ValueError:
                return f"Error: Invalid life experience level: {preference_value}. Valid options: young, developing, experienced, mature"

        elif preference_name == "communication_style":
            try:
                preferences.communication_style = CommunicationStyle(
                    preference_value.lower()
                )
            except ValueError:
                return f"Error: Invalid communication style: {preference_value}. Valid options: detailed, concise, step_by_step, motivational, practical"

        elif preference_name == "age_range":
            preferences.age_range = preference_value

        elif preference_name == "life_stage":
            preferences.life_stage = preference_value

        elif preference_name == "learning_style":
            preferences.learning_style = preference_value

        elif preference_name == "goal" or preference_name == "life_goal":
            if preference_value not in preferences.current_life_goals:
                preferences.current_life_goals.append(preference_value)

        elif preference_name == "challenge" or preference_name == "life_challenge":
            if preference_value not in preferences.current_challenges:
                preferences.current_challenges.append(preference_value)

        elif preference_name == "value" or preference_name == "core_value":
            if preference_value not in preferences.values:
                preferences.values.append(preference_value)

        elif preference_name == "life_area" or preference_name == "focus_area":
            try:
                life_area = LifeArea(preference_value.lower().replace(" ", "_"))
                if life_area not in preferences.focus_life_areas:
                    preferences.focus_life_areas.append(life_area)
            except ValueError:
                return f"Error: Invalid life area: {preference_value}. Valid options: career, relationships, health, finance, personal_growth, productivity, creativity, social, spirituality, lifestyle"

        elif preference_name == "tool" or preference_name == "preferred_tool":
            if preference_value not in preferences.preferred_tools:
                preferences.preferred_tools.append(preference_value)

        else:
            return f"Error: Unknown preference: {preference_name}. Valid preferences: name, life_experience_level, communication_style, age_range, life_stage, learning_style, goal, challenge, value, life_area, tool"

        # Update session state using ADK best practices
        service_update_user_preferences(session_state, preferences)

        return f"Successfully updated {preference_name} to: {preference_value}"

    except Exception as e:
        logger.error(f"Error setting user preference: {e}")
        return f"Error: Failed to set preference: {str(e)}"


def analyze_message_for_preferences(message: str, tool_context) -> str:
    """
    Analyze a user message to detect and update life guidance preferences automatically.

    Args:
        message: The user's message to analyze for preference indicators
        tool_context: ADK ToolContext providing access to session state

    Returns:
        str: Status message indicating what preferences were detected and updated.
    """
    try:
        # Get session state from ADK ToolContext
        session_state = getattr(tool_context, "state", {}) if tool_context else {}

        # Store original preferences for comparison
        original_prefs = service_get_user_preferences(session_state)

        # Analyze message and update preferences
        updated_prefs = service_analyze_user_message_for_preferences(
            message, session_state
        )

        # Check what changed
        changes = []

        if updated_prefs.user_name != original_prefs.user_name:
            changes.append(f"Name: {updated_prefs.user_name}")

        if updated_prefs.life_experience_level != original_prefs.life_experience_level:
            changes.append(
                f"Life Experience: {updated_prefs.life_experience_level.value}"
            )

        if updated_prefs.communication_style != original_prefs.communication_style:
            changes.append(
                f"Communication Style: {updated_prefs.communication_style.value}"
            )

        if len(updated_prefs.focus_life_areas) > len(original_prefs.focus_life_areas):
            new_areas = set(updated_prefs.focus_life_areas) - set(
                original_prefs.focus_life_areas
            )
            changes.append(f"New Life Areas: {[area.value for area in new_areas]}")

        if len(updated_prefs.preferred_tools) > len(original_prefs.preferred_tools):
            new_tools = set(updated_prefs.preferred_tools) - set(
                original_prefs.preferred_tools
            )
            changes.append(f"New Tools: {list(new_tools)}")

        if len(updated_prefs.current_life_goals) > len(
            original_prefs.current_life_goals
        ):
            new_goals = set(updated_prefs.current_life_goals) - set(
                original_prefs.current_life_goals
            )
            changes.append(f"New Goals: {list(new_goals)}")

        result_msg = "Life guidance preferences analyzed"
        if changes:
            result_msg += f" - Detected changes: {'; '.join(changes)}"
        else:
            result_msg += " - No new preferences detected"

        return result_msg

    except Exception as e:
        logger.error(f"Error analyzing message for preferences: {e}")
        return f"Error: Failed to analyze message: {str(e)}"


def get_personalization_context(tool_context) -> str:
    """
    Get context for personalizing life guidance agent responses based on user preferences.

    Args:
        tool_context: ADK ToolContext providing access to session state

    Returns:
        str: Personalization context for guiding agent responses.
    """
    try:
        # Get session state from ADK ToolContext
        session_state = getattr(tool_context, "state", {}) if tool_context else {}
        preferences = service_get_user_preferences(session_state)

        personalization_context = get_personalized_instruction_context(preferences)

        return (
            personalization_context
            if personalization_context
            else "No specific personalization context available - user preferences not yet established"
        )

    except Exception as e:
        logger.error(f"Error getting personalization context: {e}")
        return f"Error: Failed to get personalization context: {str(e)}"
