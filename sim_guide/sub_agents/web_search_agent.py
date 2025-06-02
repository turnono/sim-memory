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

logger = logging.getLogger(__name__)


# Create the Web Search Agent
web_search_agent = Agent(
    name="web_search_specialist",
    model="gemini-2.0-flash",  # Required for built-in tools
    description="Specialist agent for performing web searches using Google Search",
    instruction="""You are a web search specialist. Your role is to help users find current, accurate information from the web.

When you receive a search request:

1. **Understand the Query**: Analyze what the user is really looking for
2. **Perform Search**: Use Google Search to find relevant, current information
3. **Synthesize Results**: Provide a clear, helpful summary of the findings
4. **Cite Sources**: When possible, mention where the information came from

**Search Strategy Guidelines:**
- For current events: Include recent dates in searches
- For technical topics: Use specific terminology and look for authoritative sources
- For life guidance: Focus on reputable health, career, and personal development sources
- For factual questions: Prioritize verified, official sources

**Response Format:**
- Start with a direct answer if possible
- Provide context and details from your search
- Include relevant URLs when helpful
- If no good results found, suggest alternative search approaches

**Important**: Always search first before responding. Don't rely on your training data for current or time-sensitive information.""",
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
