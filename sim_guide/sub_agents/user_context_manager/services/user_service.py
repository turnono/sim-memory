"""
User Management Service for Life Guidance

Handles user preference detection, analysis, and session state management
following ADK best practices for user data handling.
"""

import logging
import re
from typing import Dict, Any
from datetime import datetime

from .user_models import (
    UserPreferences,
    LifeExperienceLevel,
    CommunicationStyle,
    LifeArea,
)

logger = logging.getLogger(__name__)


class UserPreferenceDetector:
    """Detects user preferences from conversation patterns focused on life guidance"""

    def __init__(self):
        # Patterns for detecting life experience level
        self.experience_patterns = {
            LifeExperienceLevel.YOUNG: [
                r"\b(young|college|university|first job|just started|new to)\b",
                r"\b(student|graduate|early twenties|early career)\b",
                r"\b(don\'t know much about|learning about|figuring out)\b",
            ],
            LifeExperienceLevel.DEVELOPING: [
                r"\b(some experience|few years|developing|growing|learning)\b",
                r"\b(mid career|building|establishing|working on)\b",
                r"\b(getting better at|improving|advancing)\b",
            ],
            LifeExperienceLevel.EXPERIENCED: [
                r"\b(experienced|established|senior|manager|leader)\b",
                r"\b(years of experience|been doing|expert in|skilled at)\b",
                r"\b(mentor|teach|guide others|lead team)\b",
            ],
            LifeExperienceLevel.MATURE: [
                r"\b(decades|many years|lifetime|wisdom|mature)\b",
                r"\b(retire|retirement|grandparent|elder|sage)\b",
                r"\b(life lessons|been through|seen it all)\b",
            ],
        }

        # Patterns for communication style
        self.communication_patterns = {
            CommunicationStyle.CONCISE: [
                r"\b(brief|short|quick|summary|bottom line|just tell me)\b",
                r"\b(cut to the chase|straight to the point|no fluff)\b",
            ],
            CommunicationStyle.DETAILED: [
                r"\b(explain everything|detailed|comprehensive|thorough)\b",
                r"\b(want to understand|why|how|background|context)\b",
            ],
            CommunicationStyle.STEP_BY_STEP: [
                r"\b(step by step|guide me|walk me through|how do I)\b",
                r"\b(one at a time|gradually|sequence|process)\b",
            ],
            CommunicationStyle.MOTIVATIONAL: [
                r"\b(motivate|inspire|encourage|uplift|positive)\b",
                r"\b(need encouragement|feeling down|boost|confidence)\b",
            ],
            CommunicationStyle.PRACTICAL: [
                r"\b(practical|actionable|what should I do|concrete steps)\b",
                r"\b(real world|hands on|actually do|implement)\b",
            ],
        }

        # Patterns for life areas
        self.life_area_patterns = {
            LifeArea.CAREER: [r"\b(career|job|work|professional|promotion|resume)\b"],
            LifeArea.RELATIONSHIPS: [
                r"\b(relationship|dating|marriage|family|friends)\b"
            ],
            LifeArea.HEALTH: [r"\b(health|fitness|exercise|mental health|wellness)\b"],
            LifeArea.FINANCE: [r"\b(money|budget|savings|investment|financial|debt)\b"],
            LifeArea.PERSONAL_GROWTH: [
                r"\b(personal growth|self improvement|learning|skills)\b"
            ],
            LifeArea.PRODUCTIVITY: [
                r"\b(productivity|time management|organization|efficiency)\b"
            ],
            LifeArea.CREATIVITY: [r"\b(creative|art|music|writing|innovation|ideas)\b"],
            LifeArea.SOCIAL: [r"\b(social|networking|communication|public speaking)\b"],
            LifeArea.SPIRITUALITY: [
                r"\b(spiritual|meaning|purpose|meditation|mindfulness)\b"
            ],
            LifeArea.LIFESTYLE: [r"\b(lifestyle|habits|routine|work life balance)\b"],
        }

        # Patterns for life tools and resources
        self.tool_patterns = {
            "calendar": [r"\b(calendar|schedule|planner|appointments)\b"],
            "journal": [r"\b(journal|diary|reflection|writing)\b"],
            "meditation": [r"\b(meditation|mindfulness|breathing|calm)\b"],
            "fitness_tracker": [r"\b(fitness tracker|steps|health app|workout)\b"],
            "budgeting_app": [r"\b(budget|expense|mint|ynab|financial app)\b"],
            "task_manager": [r"\b(todo|task|reminders|productivity app)\b"],
            "books": [r"\b(books|reading|audiobooks|learning)\b"],
            "therapy": [r"\b(therapy|counseling|therapist|mental health)\b"],
            "coaching": [r"\b(coach|mentor|guidance|advisor)\b"],
            "networking": [r"\b(networking|linkedin|professional contacts)\b"],
        }

    def detect_preferences_from_text(
        self, text: str, current_prefs: UserPreferences
    ) -> UserPreferences:
        """Analyze text and update preferences based on detected life guidance patterns"""
        text_lower = text.lower()
        updated_prefs = current_prefs

        # Detect life experience level
        experience_scores = {}
        for level, patterns in self.experience_patterns.items():
            score = sum(
                len(re.findall(pattern, text_lower, re.IGNORECASE))
                for pattern in patterns
            )
            if score > 0:
                experience_scores[level] = score

        if experience_scores:
            detected_level = max(experience_scores, key=experience_scores.get)
            confidence = experience_scores[detected_level] / len(text.split())

            if confidence > updated_prefs.preference_confidence.get(
                "life_experience_level", 0
            ):
                updated_prefs.life_experience_level = detected_level
                updated_prefs.preference_confidence["life_experience_level"] = (
                    confidence
                )
                logger.info(
                    f"Detected life experience level: {detected_level.value} (confidence: {confidence:.2f})"
                )

        # Detect communication style
        communication_scores = {}
        for style, patterns in self.communication_patterns.items():
            score = sum(
                len(re.findall(pattern, text_lower, re.IGNORECASE))
                for pattern in patterns
            )
            if score > 0:
                communication_scores[style] = score

        if communication_scores:
            detected_style = max(communication_scores, key=communication_scores.get)
            confidence = communication_scores[detected_style] / len(text.split())

            if confidence > updated_prefs.preference_confidence.get(
                "communication_style", 0
            ):
                updated_prefs.communication_style = detected_style
                updated_prefs.preference_confidence["communication_style"] = confidence
                logger.info(
                    f"Detected communication style: {detected_style.value} (confidence: {confidence:.2f})"
                )

        # Detect life areas of focus
        for life_area, patterns in self.life_area_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    if life_area not in updated_prefs.focus_life_areas:
                        updated_prefs.focus_life_areas.append(life_area)
                        logger.info(f"Detected life area interest: {life_area.value}")

        # Detect tools and resources
        for tool, patterns in self.tool_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    if tool not in updated_prefs.preferred_tools:
                        updated_prefs.preferred_tools.append(tool)
                        logger.info(f"Detected tool preference: {tool}")

        # Extract user name if mentioned
        name_patterns = [
            r"my name is (\w+)",
            r"i'm (\w+)",
            r"i am (\w+)",
            r"call me (\w+)",
        ]

        for pattern in name_patterns:
            match = re.search(pattern, text_lower)
            if match:
                name = match.group(1).capitalize()
                updated_prefs.user_name = name
                logger.info(f"Detected user name: {name}")
                break

        # Extract life goals
        goal_patterns = [
            r"my goal is to (\w.+?)(?:\.|$)",
            r"i want to (\w.+?)(?:\.|$)",
            r"hoping to (\w.+?)(?:\.|$)",
        ]

        for pattern in goal_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                if match:  # Check if match is not None or empty
                    goal = match.strip().capitalize()
                    if goal and goal not in updated_prefs.current_life_goals:
                        updated_prefs.current_life_goals.append(goal)
                        logger.info(f"Detected life goal: {goal}")

        # Update metadata
        updated_prefs.total_interactions += 1
        updated_prefs.last_updated = datetime.now().isoformat()

        return updated_prefs


def get_user_preferences(session_state: Dict[str, Any]) -> UserPreferences:
    """Get user preferences from session state using proper ADK state prefixes"""
    # Use user: prefix for user-wide preferences per ADK best practices
    prefs_data = session_state.get("user:preferences", {})
    return UserPreferences.from_dict(prefs_data)


def update_user_preferences(
    session_state: Dict[str, Any], preferences: UserPreferences
) -> None:
    """Update user preferences in session state using proper ADK state management"""
    # Store in user: prefixed state for persistence across sessions
    session_state["user:preferences"] = preferences.to_dict()
    logger.info(
        f"Updated life guidance preferences for user: {preferences.user_name or 'unknown'}"
    )


def analyze_user_message_for_preferences(
    message: str, session_state: Dict[str, Any]
) -> UserPreferences:
    """Analyze a user message and update life guidance preferences accordingly"""
    current_prefs = get_user_preferences(session_state)
    detector = UserPreferenceDetector()

    updated_prefs = detector.detect_preferences_from_text(message, current_prefs)
    update_user_preferences(session_state, updated_prefs)

    return updated_prefs


def format_preferences_summary(preferences: UserPreferences) -> str:
    """Format user preferences into a readable summary for life guidance"""
    summary_parts = []

    if preferences.user_name:
        summary_parts.append(f"Name: {preferences.user_name}")

    summary_parts.append(
        f"Life Experience: {preferences.life_experience_level.value.replace('_', ' ').title()}"
    )
    summary_parts.append(
        f"Communication Style: {preferences.communication_style.value.replace('_', ' ').title()}"
    )

    if preferences.focus_life_areas:
        life_areas = [
            area.value.replace("_", " ").title()
            for area in preferences.focus_life_areas
        ]
        summary_parts.append(f"Life Focus Areas: {', '.join(life_areas)}")

    if preferences.current_life_goals:
        summary_parts.append(
            f"Current Goals: {', '.join(preferences.current_life_goals)}"
        )

    if preferences.preferred_tools:
        tools = [tool.replace("_", " ").title() for tool in preferences.preferred_tools]
        summary_parts.append(f"Preferred Tools: {', '.join(tools)}")

    if preferences.values:
        summary_parts.append(f"Core Values: {', '.join(preferences.values)}")

    summary_parts.append(f"Total Guidance Sessions: {preferences.total_interactions}")

    return "\n".join(summary_parts)


def get_personalized_instruction_context(preferences: UserPreferences) -> str:
    """Generate context for personalizing life guidance responses based on user preferences"""
    context_parts = []

    # Life experience level context
    if preferences.life_experience_level == LifeExperienceLevel.YOUNG:
        context_parts.append(
            "User is young and starting their life journey - provide foundational guidance and encouragement."
        )
    elif preferences.life_experience_level == LifeExperienceLevel.EXPERIENCED:
        context_parts.append(
            "User is experienced in life - provide sophisticated insights and advanced strategies."
        )
    elif preferences.life_experience_level == LifeExperienceLevel.MATURE:
        context_parts.append(
            "User has mature life wisdom - engage with respect and offer perspective-based guidance."
        )

    # Communication style context
    if preferences.communication_style == CommunicationStyle.CONCISE:
        context_parts.append("User prefers brief, direct life guidance.")
    elif preferences.communication_style == CommunicationStyle.DETAILED:
        context_parts.append("User wants comprehensive life explanations and context.")
    elif preferences.communication_style == CommunicationStyle.STEP_BY_STEP:
        context_parts.append(
            "User prefers step-by-step life guidance and action plans."
        )
    elif preferences.communication_style == CommunicationStyle.MOTIVATIONAL:
        context_parts.append(
            "User responds well to encouraging and inspirational guidance."
        )
    elif preferences.communication_style == CommunicationStyle.PRACTICAL:
        context_parts.append("User wants practical, actionable life advice.")

    # Personalization
    if preferences.user_name:
        context_parts.append(f"Address user as {preferences.user_name}.")

    if preferences.focus_life_areas:
        life_areas = [
            area.value.replace("_", " ") for area in preferences.focus_life_areas
        ]
        context_parts.append(
            f"User is focused on these life areas: {', '.join(life_areas)}."
        )

    if preferences.current_life_goals:
        context_parts.append(
            f"User's current goals: {', '.join(preferences.current_life_goals)}."
        )

    if preferences.preferred_tools:
        tools = [tool.replace("_", " ") for tool in preferences.preferred_tools]
        context_parts.append(f"User prefers these life tools: {', '.join(tools)}.")

    return " ".join(context_parts) if context_parts else ""
