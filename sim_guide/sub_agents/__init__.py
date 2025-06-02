"""
Sub-Agents Module

Contains specialized sub-agents for the simulation guidance system:
- memory_agent: Handles all user context management (memory, sessions, preferences)
- capability_enhancement_agent: Provides meta-cognitive capabilities for system self-improvement
"""

from .memory_agent import memory_agent
from .capability_enhancement_agent import capability_enhancement_agent

__all__ = ["memory_agent", "capability_enhancement_agent"]
