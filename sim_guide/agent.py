from google.adk import Agent
from google.adk.tools.agent_tool import AgentTool

# Import callbacks
from .callbacks.agent import before_agent_callback, after_agent_callback
from .callbacks.model import before_model_callback, after_model_callback
from .callbacks.tool import before_tool_callback, after_tool_callback

# Import the prompt
from .prompts import PROMPT

# Import the sub_agents
from .sub_agents import user_context_manager
from .sub_agents.capability_enhancement_agent import capability_enhancement_agent
from .sub_agents.web_search_agent import web_search_agent
from .sub_agents.business_strategist_agent import business_strategist

# Import tools
from .tools import ALL_TOOLS

root_agent = Agent(
    name="sim_guide",
    model="gemini-2.0-flash",
    instruction=PROMPT,
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
    tools=[
        AgentTool(agent=user_context_manager),
        AgentTool(agent=capability_enhancement_agent),
        AgentTool(agent=web_search_agent),
        AgentTool(agent=business_strategist),
    ]
    + ALL_TOOLS,
)

# Cost-optimized agent for evaluations (no tools, minimal instruction)
eval_agent = Agent(
    name="sim_guide_eval",
    model="gemini-2.0-flash",
    instruction="""You are a helpful life guidance agent. Provide practical advice for daily life challenges, personal growth, career decisions, relationships, and life planning. Be helpful, concise, and actionable in your responses. Focus on giving useful guidance without requiring complex analysis.""",
    tools=[],  # No tools for cost optimization during evaluations
)
