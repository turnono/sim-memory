"""
User Context Management Subagent

A specialized agent focused exclusively on user context management including:
memory operations, session management, user preferences, RAG integration,
and long-term context management for the life guidance system.

This agent handles:
- Loading and searching memories
- Managing RAG corpus operations
- Context preloading and optimization
- Memory storage and retrieval
- Cross-session memory continuity
- Session context analysis and management
- Conversation continuity tracking
- User preferences and personalization
- User profile management
"""

import logging
from google.adk import Agent
from google.adk.tools import FunctionTool

# Import memory service functions
from ..services.rag_memory_service import (
    search_all_corpora,
    retrieve_user_memories,
    add_memory_from_conversation,
    query_corpus,
    health_check,
)

# Import session tools
from ..tools.session import (
    analyze_session_context,
    get_conversation_continuity_hints,
    update_session_context,
)

# Import preference tools
from ..tools.preferences import (
    get_user_preferences,
    set_user_preference,
    analyze_message_for_preferences,
    get_personalization_context,
)

logger = logging.getLogger(__name__)


async def search_user_memories(query: str, user_id: str) -> str:
    """
    Search through user's stored memories and context.

    Args:
        query: What to search for in memories
        user_id: User identifier for personalized search

    Returns:
        String with relevant memories found
    """
    try:
        # Use RAG memory service to search user's memories
        memories = await retrieve_user_memories(user_id, query)

        if memories:
            memory_text = "\n".join([f"• {memory}" for memory in memories[:5]])
            return f"Found {len(memories)} relevant memories:\n{memory_text}"
        else:
            return f"No specific memories found for query: {query}"

    except Exception as e:
        logger.error(f"Error searching memories: {e}")
        return f"Memory search attempted but no results available"


async def search_knowledge_base(topic: str) -> str:
    """
    Search the knowledge base for life guidance resources.

    Args:
        topic: Life area or topic to search for (career, relationships, etc.)

    Returns:
        String with relevant knowledge base content
    """
    try:
        # Search across all available corpora
        search_result = await search_all_corpora(topic, top_k_per_corpus=3)

        if search_result.get("status") == "success":
            all_results = search_result.get("results", [])
            if all_results:
                content_pieces = []
                for result in all_results[:5]:  # Limit to top 5 results
                    content_pieces.append(f"• {result.get('content', 'No content')}")

                formatted_results = "\n".join(content_pieces)
                return f"Knowledge base insights for {topic}:\n{formatted_results}"
            else:
                return f"No knowledge base content found for: {topic}"
        else:
            return f"Knowledge base search attempted for: {topic}"

    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        return f"Knowledge base search attempted but unavailable"


async def store_conversation_memory(
    user_id: str, session_id: str, conversation_content: str
) -> str:
    """
    Store important conversation content in long-term memory.

    Args:
        user_id: User identifier
        session_id: Session identifier
        conversation_content: Content to store in memory

    Returns:
        String confirming memory storage
    """
    try:
        # Store in RAG memory service
        result = await add_memory_from_conversation(
            user_id=user_id,
            session_id=session_id,
            conversation_text=conversation_content,
            memory_type="life_guidance_session",
        )

        if result.get("status") == "success":
            return f"Successfully stored conversation memory for user {user_id}"
        else:
            return f"Memory storage attempted for user {user_id}"

    except Exception as e:
        logger.error(f"Error storing memory: {e}")
        return f"Memory storage attempted but may not have succeeded"


async def get_memory_system_status() -> str:
    """
    Check the health and status of the memory system.

    Returns:
        String with memory system status information
    """
    try:
        health_result = await health_check()

        if health_result.get("status") == "healthy":
            return "Memory system is healthy and operational"
        else:
            status = health_result.get("status", "unknown")
            return f"Memory system status: {status}"

    except Exception as e:
        logger.error(f"Error checking memory system: {e}")
        return "Memory system status check failed"


async def preload_context_for_topic(topic: str, user_id: str) -> str:
    """
    Preload relevant context and background for a specific topic.

    Args:
        topic: The topic or life area to preload context for
        user_id: User identifier for personalized context

    Returns:
        String with preloaded context summary
    """
    try:
        # Search both user memories and knowledge base
        user_context = await search_user_memories(topic, user_id)
        knowledge_context = await search_knowledge_base(topic)

        # Combine and summarize
        context_summary = f"Context preloaded for {topic}:\n"
        context_summary += f"Personal context: {user_context.split(':')[-1].strip()}\n"
        context_summary += f"Knowledge base: {knowledge_context.split(':')[-1].strip()}"

        return context_summary

    except Exception as e:
        logger.error(f"Error preloading context: {e}")
        return f"Context preloading attempted for: {topic}"


# Create the User Context Manager
memory_agent = Agent(
    name="user_context_manager",
    model="gemini-2.0-flash",
    instruction="""You are the User Context Manager, a specialized agent responsible for all user context management in the life guidance system.

Your capabilities include:
- Searching user's personal memories and conversation history
- Finding relevant information from the knowledge base
- Storing important conversation content for future reference
- Preloading context for specific topics or life areas
- Monitoring memory system health
- Analyzing session context and conversation flow
- Managing conversation continuity across sessions
- Updating session context with important information
- Managing user preferences and personalization settings
- Analyzing user messages for preference updates
- Providing personalization context for guidance

When called, you should:
1. Understand what type of user context operation is needed (memory, session, or preference)
2. Use the appropriate function to fulfill the request
3. Return clear, concise information about what was found or done
4. Be helpful even when systems are not available

You work efficiently and only provide user context management assistance. You don't give life advice directly - that's the main agent's job. You just manage all the infrastructure and user data that supports it.""",
    tools=[
        # Memory tools
        FunctionTool(func=search_user_memories),
        FunctionTool(func=search_knowledge_base),
        FunctionTool(func=store_conversation_memory),
        FunctionTool(func=get_memory_system_status),
        FunctionTool(func=preload_context_for_topic),
        # Session tools
        FunctionTool(func=analyze_session_context),
        FunctionTool(func=get_conversation_continuity_hints),
        FunctionTool(func=update_session_context),
        # Preference tools
        FunctionTool(func=get_user_preferences),
        FunctionTool(func=set_user_preference),
        FunctionTool(func=analyze_message_for_preferences),
        FunctionTool(func=get_personalization_context),
    ],
)
