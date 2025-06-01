from google.adk.agents import Agent
from .callbacks import (
    before_agent_callback, after_agent_callback,
    before_model_callback, after_model_callback, 
    before_tool_callback, after_tool_callback
)

# Create the agent with callbacks registered for comprehensive monitoring
root_agent = Agent(
    name="sim_guide",
    model="gemini-2.0-flash",
    instruction="You are a personal guide that helps with daily life and long-term goals.",
    # Register callbacks through constructor parameters (the correct ADK way)
    before_agent_callback=before_agent_callback,
    after_agent_callback=after_agent_callback,
    before_model_callback=before_model_callback,
    after_model_callback=after_model_callback,
    before_tool_callback=before_tool_callback,
    after_tool_callback=after_tool_callback,
    output_key="sim_guide_output",
)