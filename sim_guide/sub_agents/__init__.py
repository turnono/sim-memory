"""
Sub-Agents Module

Contains specialized sub-agents for the simulation guidance system:
- memory_agent: Handles all user context management (memory, sessions, preferences)
- capability_enhancement_agent: Provides meta-cognitive capabilities for system self-improvement
- web_search_agent: Performs web searches using Google's built-in search tool (used as AgentTool)
"""

from .memory_agent import memory_agent
from .capability_enhancement_agent import capability_enhancement_agent
from .web_search_agent import web_search_agent

__all__ = ["memory_agent", "capability_enhancement_agent", "web_search_agent"]
