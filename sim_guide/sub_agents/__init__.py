"""
Sub-Agents Module

Contains specialized sub-agents for the simulation guidance system:
- memory_manager: Handles memory management (memory, sessions)
- capability_enhancement_agent: Provides meta-cognitive capabilities for system self-improvement
- web_search_agent: Performs web searches using Google's built-in search tool (used as AgentTool)
- business_strategist_agent: MBA-level business strategy with hierarchical sub-agents
"""

from .memory_manager import memory_manager
from .capability_enhancement import capability_enhancement_agent
from .web_search import web_search_agent
from .business_strategist import business_strategist, get_business_strategist

__all__ = [
    "memory_manager",
    "capability_enhancement_agent",
    "web_search_agent",
    "business_strategist",
    "get_business_strategist",
]
