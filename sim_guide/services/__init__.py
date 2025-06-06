"""
Services Module for Life Guidance

Root-level services. All memory management services have been moved
to the memory_manager sub-agent services directory:

- Memory configuration → sim_guide.sub_agents.memory_manager.services.rag_memory_service
- Session service → sim_guide.sub_agents.memory_manager.services.session_service

Note: Memory functionality now uses ADK's built-in load_memory tool.
"""

# All memory management services have been moved to the memory_manager sub-agent
# Import them from: sim_guide.sub_agents.memory_manager.services

__all__ = [
    # No services remain at root level - all moved to appropriate sub-agents
]
