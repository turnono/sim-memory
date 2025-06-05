"""
Web Search Agent

A specialized agent that uses Google's built-in search tool to perform web searches.
This agent is designed to be used as an AgentTool in the main agent, respecting
ADK limitations around built-in tools in sub-agents.

Key ADK Compliance:
- Uses google_search built-in tool (requires Gemini 2.0 model)
- Cannot be used as a sub-agent (ADK limitation)
- Must be used as an AgentTool in the root agent
- Only uses one built-in tool (no mixing with other tools)
"""

import logging
from google.adk import Agent
from google.adk.tools import google_search

# Import prompts
from .prompt import DESCRIPTION, INSTRUCTION

logger = logging.getLogger(__name__)


# Create the Web Search Agent
web_search_agent = Agent(
    name="web_search_agent",
    model="gemini-2.0-flash",  # Required for built-in tools
    description=DESCRIPTION,
    instruction=INSTRUCTION,
    output_key="web_search_result",  # String key for search results
    tools=[google_search],  # Uses Google's built-in search tool
)


def get_web_search_agent():
    """
    Returns the web search agent for use as an AgentTool.

    Returns:
        Agent: The configured web search agent with google_search tool
    """
    return web_search_agent


# Export for use in main agent
__all__ = ["web_search_agent", "get_web_search_agent"]
