"""
Services Module for Life Guidance

Root-level services. All user context management services have been moved
to the user_context_manager sub-agent services directory:

- User preference services → sim_guide.sub_agents.user_context_manager.services.user_service
- User models → sim_guide.sub_agents.user_context_manager.services.user_models
- RAG memory service → sim_guide.sub_agents.user_context_manager.services.rag_memory_service
- Session service → sim_guide.sub_agents.user_context_manager.services.session_service
"""

# All user context management services have been moved to the user_context_manager sub-agent
# Import them from: sim_guide.sub_agents.user_context_manager.services

__all__ = [
    # No services remain at root level - all moved to appropriate sub-agents
]
