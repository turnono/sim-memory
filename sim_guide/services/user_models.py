"""
User Data Models for Life Guidance

Defines the core data structures for user preferences, life areas,
and communication styles used throughout the life guidance system.
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum


class LifeExperienceLevel(Enum):
    """User life experience levels"""

    YOUNG = "young"  # Young adults, early career
    DEVELOPING = "developing"  # Building life skills, mid-career
    EXPERIENCED = "experienced"  # Established in life, senior career
    MATURE = "mature"  # Life wisdom, mentoring others


class CommunicationStyle(Enum):
    """User communication preferences"""

    DETAILED = "detailed"  # Comprehensive explanations and context
    CONCISE = "concise"  # Brief, to-the-point guidance
    STEP_BY_STEP = "step_by_step"  # Guided, sequential instructions
    MOTIVATIONAL = "motivational"  # Encouraging, inspirational tone
    PRACTICAL = "practical"  # Direct, actionable advice


class LifeArea(Enum):
    """Areas of life the user needs guidance in"""

    CAREER = "career"  # Professional development, job search
    RELATIONSHIPS = "relationships"  # Personal relationships, family
    HEALTH = "health"  # Physical and mental wellbeing
    FINANCE = "finance"  # Money management, investments
    PERSONAL_GROWTH = "personal_growth"  # Self-improvement, learning
    PRODUCTIVITY = "productivity"  # Time management, organization
    CREATIVITY = "creativity"  # Artistic pursuits, innovation
    SOCIAL = "social"  # Social skills, networking
    SPIRITUALITY = "spirituality"  # Meaning, purpose, beliefs
    LIFESTYLE = "lifestyle"  # Daily habits, life balance


@dataclass
class UserPreferences:
    """Structured user preferences for life guidance"""

    # Core preferences
    user_name: Optional[str] = None
    life_experience_level: LifeExperienceLevel = LifeExperienceLevel.DEVELOPING
    communication_style: CommunicationStyle = CommunicationStyle.DETAILED

    # Life guidance preferences
    focus_life_areas: List[LifeArea] = None
    current_life_goals: List[str] = None
    current_challenges: List[str] = None

    # Personal context
    age_range: Optional[str] = None  # "20s", "30s", "40s", etc.
    life_stage: Optional[str] = (
        None  # "student", "early_career", "parent", "retired", etc.
    )
    values: List[str] = None  # Core values that guide decisions

    # Guidance preferences
    prefers_examples: bool = True
    wants_action_plans: bool = True
    likes_motivation: bool = True

    # Tools and resources preferences
    preferred_tools: List[str] = None  # Apps, methods, frameworks they use
    learning_style: Optional[str] = None  # "visual", "auditory", "hands_on", "reading"

    # Interaction history
    total_interactions: int = 0
    last_updated: Optional[str] = None
    preference_confidence: Dict[str, float] = (
        None  # Confidence scores for auto-detected preferences
    )

    def __post_init__(self):
        """Initialize default values for mutable fields"""
        if self.focus_life_areas is None:
            self.focus_life_areas = []
        if self.current_life_goals is None:
            self.current_life_goals = []
        if self.current_challenges is None:
            self.current_challenges = []
        if self.values is None:
            self.values = []
        if self.preferred_tools is None:
            self.preferred_tools = []
        if self.preference_confidence is None:
            self.preference_confidence = {}
        if self.last_updated is None:
            self.last_updated = datetime.now().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        """Convert preferences to dictionary for session storage"""
        result = asdict(self)

        # Convert enums to strings for serialization
        result["life_experience_level"] = self.life_experience_level.value
        result["communication_style"] = self.communication_style.value
        result["focus_life_areas"] = [area.value for area in self.focus_life_areas]

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserPreferences":
        """Create preferences from dictionary stored in session state"""
        if not data:
            return cls()

        # Convert string enums back to enum objects
        if "life_experience_level" in data:
            data["life_experience_level"] = LifeExperienceLevel(
                data["life_experience_level"]
            )

        if "communication_style" in data:
            data["communication_style"] = CommunicationStyle(
                data["communication_style"]
            )

        if "focus_life_areas" in data:
            data["focus_life_areas"] = [
                LifeArea(area) for area in data["focus_life_areas"]
            ]

        return cls(**data)
