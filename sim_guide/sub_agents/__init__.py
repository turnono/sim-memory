"""
Sub-Agents Module

Contains specialized sub-agents for the simulation guidance system:
- user_context_manager: Handles all user context management (memory, sessions, preferences)
- capability_enhancement_agent: Provides meta-cognitive capabilities for system self-improvement
- web_search_agent: Performs web searches using Google's built-in search tool (used as AgentTool)
- business_strategist_agent: MBA-level business strategy with hierarchical sub-agents
"""

from .user_context_manager import user_context_manager
from .capability_enhancement_agent import capability_enhancement_agent
from .web_search_agent import web_search_agent
from .business_strategist_agent import business_strategist, get_business_strategist

__all__ = [
    "user_context_manager",
    "capability_enhancement_agent",
    "web_search_agent",
    "business_strategist",
    "get_business_strategist",
]
