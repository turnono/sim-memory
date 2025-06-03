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

# Import business strategy tools
from .business_strategy import (
    get_business_strategy_advice,
    analyze_business_opportunity,
    get_business_strategic_plan,
    get_competitive_analysis,
)

# Create FunctionTool instances for preference tools
preference_tools = [
    FunctionTool(func=get_user_preferences),
    FunctionTool(func=set_user_preference),
    FunctionTool(func=analyze_message_for_preferences),
    FunctionTool(func=get_personalization_context),
]

# Create FunctionTool instances for business strategy tools
business_strategy_tools = [
    FunctionTool(func=get_business_strategy_advice),
    FunctionTool(func=analyze_business_opportunity),
    FunctionTool(func=get_business_strategic_plan),
    FunctionTool(func=get_competitive_analysis),
]

# Combine all tools
ALL_TOOLS = preference_tools + business_strategy_tools

# Export for easy import
__all__ = ["ALL_TOOLS", "preference_tools", "business_strategy_tools"]
