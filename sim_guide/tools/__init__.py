"""
Life Guidance Tools Module

This module registers function-based tools for the life guidance agent
following Google ADK best practices using FunctionTool.

Note: All agent-specific tools have been moved to their respective sub-agents:
- Memory, session, and preference tools are now handled by the user_context_manager subagent
- Business strategy tools are now handled by the business_strategist subagent
- The root agent now only coordinates through sub-agents
"""


# No direct tools for root agent - all functionality is handled by sub-agents
ALL_TOOLS = []

# Export for easy import
__all__ = ["ALL_TOOLS"]
