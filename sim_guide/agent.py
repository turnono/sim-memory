from google.adk.agents import Agent

# Create the agent - clean and focused
root_agent = Agent(
    name="sim_guide",
    model="gemini-2.0-flash",
    instruction="You are a helpful agent who can guide users through simulations. You help users understand how to set up, run, and monitor simulations effectively.",
)