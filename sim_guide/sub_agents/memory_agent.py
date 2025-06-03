"""
User Context Management Subagent

A specialized agent focused exclusively on user context management including:
memory operations, session management, user preferences, RAG integration,
and long-term context management for the life guidance system.

This agent handles:
- Loading and searching memories with ADK-aligned hybrid routing
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

# Import existing memory service functions (now with hybrid capabilities)
from ..services.rag_memory_service import (
    search_all_corpora,
    retrieve_user_memories,
    add_memory_from_conversation,
    query_corpus,
    health_check,
    search_memories_hybrid,  # New ADK-aligned hybrid function
    classify_query_complexity,  # Simple classification
    HYBRID_CONFIG,  # Configuration
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


# === HYBRID MEMORY FUNCTIONS ===


async def search_user_memories_hybrid(query: str, tool_context=None) -> str:
    """
    Search through user's stored memories using ADK-aligned intelligent routing.
    Automatically chooses between keyword search and semantic RAG based on query type.

    Args:
        query: What to search for in memories (can be simple or complex)
        tool_context: ADK ToolContext providing access to session context including user_id

    Returns:
        String with relevant memories found and method transparency
    """
    try:
        # Get user_id from session context
        user_id = "unknown_user"  # Default fallback
        if (
            tool_context
            and hasattr(tool_context, "session")
            and hasattr(tool_context.session, "user_id")
        ):
            user_id = tool_context.session.user_id
        elif tool_context and hasattr(tool_context, "user_id"):
            user_id = tool_context.user_id

        # Use ADK-aligned hybrid search from existing service
        result = await search_memories_hybrid(user_id, query)

        if result["status"] == "success" and result["memories"]:
            memories = result["memories"]
            memory_text = "\n".join([f"• {memory}" for memory in memories])

            response = f"Found {len(memories)} relevant memories:\n{memory_text}"

            # Add transparent communication if available
            if result.get("message"):
                response += f"\n\n{result['message']}"

            return response
        else:
            return f"No specific memories found for query: {query}"

    except Exception as e:
        logger.error(f"Error in hybrid memory search: {e}")
        # Fallback to original memory search
        try:
            memories = await retrieve_user_memories(user_id, query)
            if memories:
                memory_text = "\n".join([f"• {memory}" for memory in memories])
                return f"Found {len(memories)} relevant memories (fallback mode):\n{memory_text}"
            else:
                return f"No memories found for query: {query}"
        except Exception as fallback_error:
            logger.error(f"Fallback memory search also failed: {fallback_error}")
            return f"Memory search attempted but temporarily unavailable"


async def store_conversation_memory_hybrid(
    conversation_content: str, memory_type: str = "general", tool_context=None
) -> str:
    """
    Store conversation memory using the existing RAG service.

    Args:
        conversation_content: Content of the conversation to store
        memory_type: Type of memory (general, milestone, goal, etc.)
        tool_context: ADK ToolContext providing access to session context

    Returns:
        String confirmation of storage
    """
    try:
        # Get user_id and session_id from context
        user_id = "unknown_user"
        session_id = "unknown_session"

        if (
            tool_context
            and hasattr(tool_context, "session")
            and hasattr(tool_context.session, "user_id")
        ):
            user_id = tool_context.session.user_id
            session_id = getattr(tool_context.session, "session_id", "unknown_session")
        elif tool_context and hasattr(tool_context, "user_id"):
            user_id = tool_context.user_id

        # Use existing memory service
        result = await add_memory_from_conversation(
            user_id, session_id, conversation_content, memory_type
        )

        if result.get("status") == "success":
            return f"✅ Conversation memory stored successfully: {result.get('message', '')}"
        else:
            return (
                f"❌ Failed to store memory: {result.get('message', 'Unknown error')}"
            )

    except Exception as e:
        logger.error(f"Error in memory storage: {e}")
        return f"❌ Memory storage temporarily unavailable: {str(e)}"


async def search_for_deep_insights(query: str, tool_context=None) -> str:
    """
    Search for deep insights and patterns using semantic analysis.
    Forces semantic search for complex analysis.

    Args:
        query: Complex query requiring semantic understanding
        tool_context: ADK ToolContext providing access to session context

    Returns:
        String with deep insights and analysis
    """
    try:
        # Get user_id from session context
        user_id = "unknown_user"
        if (
            tool_context
            and hasattr(tool_context, "session")
            and hasattr(tool_context.session, "user_id")
        ):
            user_id = tool_context.session.user_id
        elif tool_context and hasattr(tool_context, "user_id"):
            user_id = tool_context.user_id

        # Force semantic search for deep insights
        result = await search_memories_hybrid(user_id, query, force_semantic=True)

        if result["status"] == "success" and result["memories"]:
            memories = result["memories"]
            memory_text = "\n".join([f"• {memory}" for memory in memories])

            response = f"🧠 Deep Analysis Results ({len(memories)} insights found):\n{memory_text}"

            # Add method info
            if result.get("message"):
                response += f"\n\n{result['message']}"

            return response
        else:
            return f"🧠 Deep analysis attempted but no insights found."

    except Exception as e:
        logger.error(f"Error in deep insights search: {e}")
        return f"🧠 Deep analysis temporarily unavailable: {str(e)}"


async def get_memory_usage_report(tool_context=None) -> str:
    """
    Get current memory configuration and status.

    Returns:
        String with configuration report
    """
    try:
        return f"""📊 Memory System Status:

**Configuration:**
• Hybrid Mode: {"Enabled" if HYBRID_CONFIG["enabled"] else "Disabled"}
• Semantic Keywords: {len(HYBRID_CONFIG["semantic_keywords"])} patterns
• Transparent Communication: {"Enabled" if HYBRID_CONFIG["transparent_communication"] else "Disabled"}

**Routing:**
• Simple queries use keyword search (fast, low cost)
• Complex queries use semantic search (powerful, higher cost)
• Classification based on query patterns"""

    except Exception as e:
        logger.error(f"Error getting usage report: {e}")
        return f"📊 Usage report temporarily unavailable: {str(e)}"


async def check_hybrid_memory_health(tool_context=None) -> str:
    """
    Check the health status of the memory system.

    Returns:
        String with health status and configuration
    """
    try:
        health = await health_check()

        status_emoji = {"healthy": "✅", "degraded": "⚠️", "unhealthy": "❌"}.get(
            health.get("status"), "❓"
        )

        response = f"""{status_emoji} Memory System Status: {health.get("status", "unknown").upper()}

**Message:** {health.get("message", "No details available")}

**Hybrid Configuration:**
• Mode: {"Enabled" if HYBRID_CONFIG["enabled"] else "Disabled"}
• Transparent Communication: {"Enabled" if HYBRID_CONFIG["transparent_communication"] else "Disabled"}
• Auto-routing: Simple→Keyword, Complex→Semantic"""

        return response

    except Exception as e:
        logger.error(f"Error checking memory health: {e}")
        return f"❌ Health check failed: {str(e)}"


# === EXISTING FUNCTIONS (Updated to use hybrid when possible) ===


async def search_user_memories(query: str, tool_context=None) -> str:
    """
    Search through user's stored memories and context.
    Now uses hybrid memory service by default.

    Args:
        query: What to search for in memories
        tool_context: ADK ToolContext providing access to session context including user_id

    Returns:
        String with relevant memories found
    """
    # Delegate to hybrid version
    return await search_user_memories_hybrid(query, tool_context)


async def store_conversation_memory(
    conversation_content: str, memory_type: str = "general", tool_context=None
) -> str:
    """
    Store conversation content as memory for future reference.
    Now uses hybrid memory service by default.

    Args:
        conversation_content: Content of the conversation to store
        memory_type: Type of memory (general, preference, goal, etc.)
        tool_context: ADK ToolContext providing access to session context

    Returns:
        String confirmation of storage
    """
    # Delegate to hybrid version
    return await store_conversation_memory_hybrid(
        conversation_content, memory_type, tool_context
    )


async def search_meaningful_memories(query: str, tool_context=None) -> str:
    """
    Search for meaningful conversation memories using semantic understanding.
    Examples: "times user felt stressed", "advice about career", "progress on goals"

    Args:
        query: Semantic search query for finding relevant past conversations
        tool_context: ADK ToolContext providing access to session context including user_id

    Returns:
        String with relevant meaningful memories found
    """
    # Use the deep insights function for semantic queries
    return await search_for_deep_insights(query, tool_context)


# === ORIGINAL FUNCTIONS (maintained for compatibility) ===


async def search_knowledge_base(query: str, tool_context=None) -> str:
    """
    Search through general knowledge base and available corpora.

    Args:
        query: What to search for in knowledge base
        tool_context: ADK ToolContext (optional)

    Returns:
        String with relevant knowledge found
    """
    try:
        # Search across all available corpora
        search_result = await search_all_corpora(query)

        if search_result.get("status") == "success" and search_result.get("results"):
            results_text = "\n".join(
                [f"• {result}" for result in search_result["results"]]
            )
            return f"Found {len(search_result['results'])} knowledge base results:\n{results_text}"
        else:
            return f"No knowledge base results found for: {query}"

    except Exception as e:
        logger.error(f"Error searching knowledge base: {e}")
        return f"Knowledge base search attempted but no results available"


async def preload_context_for_topic(topic: str, tool_context=None) -> str:
    """
    Preload relevant context and background for a specific topic.

    Args:
        topic: The topic or life area to preload context for
        tool_context: ADK ToolContext providing access to session context including user_id

    Returns:
        String with preloaded context summary
    """
    try:
        # Get user_id from session context
        user_id = "unknown_user"  # Default fallback
        if (
            tool_context
            and hasattr(tool_context, "session")
            and hasattr(tool_context.session, "user_id")
        ):
            user_id = tool_context.session.user_id
        elif tool_context and hasattr(tool_context, "user_id"):
            user_id = tool_context.user_id

        # Search both user memories and knowledge base
        user_context = await search_user_memories(topic, tool_context)
        knowledge_context = await search_knowledge_base(topic)

        # Combine and summarize
        context_summary = f"Context preloaded for {topic}:\n"
        context_summary += f"Personal context: {user_context.split(':')[-1].strip()}\n"
        context_summary += f"Knowledge base: {knowledge_context.split(':')[-1].strip()}"

        return context_summary

    except Exception as e:
        logger.error(f"Error preloading context: {e}")
        return f"Context preloading attempted for: {topic}"


# === MEMORY AGENT CONFIGURATION ===

# Memory management tools using hybrid service
memory_tools = [
    FunctionTool(func=search_user_memories_hybrid),
    FunctionTool(func=store_conversation_memory_hybrid),
    FunctionTool(func=search_for_deep_insights),
    FunctionTool(func=get_memory_usage_report),
    FunctionTool(func=check_hybrid_memory_health),
    FunctionTool(func=search_knowledge_base),
    FunctionTool(func=preload_context_for_topic),
]

# Session management tools
session_tools = [
    FunctionTool(func=analyze_session_context),
    FunctionTool(func=get_conversation_continuity_hints),
    FunctionTool(func=update_session_context),
]

# User preference tools
preference_tools = [
    FunctionTool(func=get_user_preferences),
    FunctionTool(func=set_user_preference),
    FunctionTool(func=analyze_message_for_preferences),
    FunctionTool(func=get_personalization_context),
]

# Combine all tools
all_memory_tools = memory_tools + session_tools + preference_tools

# Memory Management Agent
memory_agent = Agent(
    name="memory_agent",
    model="gemini-2.0-flash",
    description="""
    Specialized agent for comprehensive user context management with hybrid memory approach.
    
    **Key Capabilities:**
    - Intelligent memory routing (keyword search for simple queries, semantic RAG for deep analysis)
    - Cost-effective storage with selective RAG import based on content importance  
    - Transparent communication about memory methods used
    - Usage tracking and limit enforcement
    - Cross-session memory continuity
    - User preference management
    - Session context analysis
    
    **Hybrid Memory Features:**
    - Automatically chooses optimal search method based on query type
    - Provides usage reports and recommendations
    - Supports both cost-optimized and high-quality modes
    - Maintains compatibility with existing memory operations
    
    This agent ensures efficient, cost-effective memory operations while preserving the ability
    to provide deep insights when needed for life guidance and pattern recognition.
    """,
    instruction="""
    You are the Memory Management Agent responsible for all user context operations.
    
    **Memory Operation Guidelines:**
    
    1. **Query Routing:**
       - Simple queries (recent events, quick lookups): Automatically use keyword search
       - Complex queries (patterns, analysis, reviews): Automatically use semantic search
       - Respect daily/weekly semantic search limits
       - Inform user transparently about method used
    
    2. **Storage Decisions:**
       - Routine conversations: Store in GCS only (cost-effective)
       - Important/milestone content: Store with RAG import (semantic capability)
       - Always provide transparent feedback about storage method
    
    3. **Cost Management:**
       - Monitor usage statistics and inform users of remaining limits
       - Suggest cost-effective alternatives when limits are reached
       - Provide usage reports when requested
    
    4. **User Communication:**
       - Be transparent about which memory method is being used
       - Explain why a particular method was chosen
       - Provide helpful suggestions for optimal memory usage
    
    5. **Error Handling:**
       - Gracefully fallback to keyword search if semantic search fails
       - Provide clear error messages with actionable next steps
       - Maintain service availability even when some components are degraded
    
    **Available Functions:**
    - search_memories: Intelligent memory search with automatic routing
    - store_memory: Smart storage with selective RAG import
    - search_deep_insights: Force semantic analysis for complex queries
    - memory_usage_report: Get usage statistics and recommendations
    - check_memory_health: Check system health and configuration
    - Various session and preference management functions
    
    Always prioritize user experience while maintaining cost efficiency.
    """,
    tools=all_memory_tools,
)
