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


async def store_user_info(info_type: str, info_value: str, tool_context=None) -> str:
    """
    Store user information in session state for immediate access during the session.

    Args:
        info_type: Type of information (e.g., 'name', 'profession', 'location', 'goal')
        info_value: The information value to store
        tool_context: ADK ToolContext providing access to session state

    Returns:
        String confirming information storage
    """
    try:
        if not tool_context or not hasattr(tool_context, "state"):
            return (
                f"Session state not available - cannot store {info_type}: {info_value}"
            )

        # Store in session state (ADK recommended approach)
        if "user_profile" not in tool_context.state:
            tool_context.state["user_profile"] = {}

        tool_context.state["user_profile"][info_type] = info_value

        return f"Successfully stored {info_type}: {info_value} in session"

    except Exception as e:
        logger.error(f"Error storing user info in session: {e}")
        return f"Failed to store {info_type}: {info_value}"


async def get_user_info(info_type: str, tool_context=None) -> str:
    """
    Retrieve user information from session state first, then fallback to long-term memory.

    Args:
        info_type: Type of information to retrieve
        tool_context: ADK ToolContext providing access to session state

    Returns:
        String with the requested information or indication if not found
    """
    try:
        # First check session state (current session data)
        if tool_context and hasattr(tool_context, "state"):
            user_profile = tool_context.state.get("user_profile", {})
            if info_type in user_profile:
                value = user_profile[info_type]
                return f"Found {info_type}: {value} (from current session)"

        # Fallback to long-term memory for cross-session data
        user_id = "unknown_user"
        if (
            tool_context
            and hasattr(tool_context, "session")
            and hasattr(tool_context.session, "user_id")
        ):
            user_id = tool_context.session.user_id
        elif tool_context and hasattr(tool_context, "user_id"):
            user_id = tool_context.user_id

        # Search long-term memory
        memories = await retrieve_user_memories(user_id, info_type)
        if memories:
            relevant_memories = []
            memory_limit = min(len(memories), 3)
            for memory in memories[:memory_limit]:
                if info_type.lower() in memory.lower():
                    relevant_memories.append(memory)

            if relevant_memories:
                return f"Found {info_type} from previous sessions:\n" + "\n".join(
                    [f"• {mem}" for mem in relevant_memories]
                )

        return f"No {info_type} information found in session or memory"

    except Exception as e:
        logger.error(f"Error retrieving user info: {e}")
        return f"Information retrieval failed for {info_type}"


async def get_all_user_context(tool_context=None) -> str:
    """
    Get comprehensive user context from both session state and long-term memory.

    Args:
        tool_context: ADK ToolContext providing access to session state

    Returns:
        String with comprehensive user context
    """
    try:
        context_parts = []

        # Get current session context
        if tool_context and hasattr(tool_context, "state"):
            user_profile = tool_context.state.get("user_profile", {})
            if user_profile:
                context_parts.append("Current session information:")
                for info_type, info_value in user_profile.items():
                    context_parts.append(f"• {info_type}: {info_value}")

        # Get historical context from long-term memory
        user_id = "unknown_user"
        if (
            tool_context
            and hasattr(tool_context, "session")
            and hasattr(tool_context.session, "user_id")
        ):
            user_id = tool_context.session.user_id
        elif tool_context and hasattr(tool_context, "user_id"):
            user_id = tool_context.user_id

        # Search for common user info types in long-term memory
        info_types = ["name", "profession", "location", "goal", "interest", "skill"]
        historical_context = []

        for info_type in info_types:
            memories = await retrieve_user_memories(user_id, info_type)
            if memories:
                historical_context.append(f"Historical {info_type}: {memories[0]}")

        if historical_context:
            context_parts.append("\nPrevious session information:")
            context_parts.extend([f"• {ctx}" for ctx in historical_context])

        if context_parts:
            return "\n".join(context_parts)
        else:
            return "No user context found - this appears to be a new user with no previous sessions"

    except Exception as e:
        logger.error(f"Error getting user context: {e}")
        return "User context retrieval failed"


async def save_session_to_memory(tool_context=None) -> str:
    """
    Save current session data to long-term memory (call at session end).

    Args:
        tool_context: ADK ToolContext providing access to session state

    Returns:
        String confirming memory storage
    """
    try:
        if not tool_context or not hasattr(tool_context, "state"):
            return "Session state not available - cannot save to memory"

        user_id = "unknown_user"
        if hasattr(tool_context, "session") and hasattr(
            tool_context.session, "user_id"
        ):
            user_id = tool_context.session.user_id
        elif hasattr(tool_context, "user_id"):
            user_id = tool_context.user_id

        session_id = (
            getattr(tool_context.session, "session_id", "unknown_session")
            if hasattr(tool_context, "session")
            else "unknown_session"
        )

        # Get user profile from session state
        user_profile = tool_context.state.get("user_profile", {})

        if not user_profile:
            return "No user profile data in session to save"

        # Convert session data to conversation text for memory storage
        profile_text = "User profile information: "
        profile_items = []
        for info_type, info_value in user_profile.items():
            profile_items.append(f"{info_type}: {info_value}")

        profile_text += ", ".join(profile_items)

        # Store in long-term memory
        result = await add_memory_from_conversation(
            user_id=user_id,
            session_id=session_id,
            conversation_text=profile_text,
            memory_type="user_profile_data",
        )

        if result.get("status") == "success":
            return f"Successfully saved session data to long-term memory for user {user_id}"
        else:
            return f"Attempted to save session data to memory for user {user_id}"

    except Exception as e:
        logger.error(f"Error saving session to memory: {e}")
        return "Failed to save session data to memory"


async def get_session_state_summary(tool_context=None) -> str:
    """
    Get a summary of what's currently stored in session state.

    Args:
        tool_context: ADK ToolContext providing access to session state

    Returns:
        String with session state summary
    """
    try:
        if not tool_context or not hasattr(tool_context, "state"):
            return "Session state not available"

        state_summary = []

        # Check user profile
        user_profile = tool_context.state.get("user_profile", {})
        if user_profile:
            state_summary.append("User Profile in Session:")
            for info_type, info_value in user_profile.items():
                state_summary.append(f"• {info_type}: {info_value}")

        # Check other session data
        other_keys = [key for key in tool_context.state.keys() if key != "user_profile"]
        if other_keys:
            state_summary.append("Other Session Data:")
            for key in other_keys:
                state_summary.append(f"• {key}: {tool_context.state[key]}")

        if state_summary:
            return "\n".join(state_summary)
        else:
            return "Session state is empty"

    except Exception as e:
        logger.error(f"Error getting session state summary: {e}")
        return "Failed to retrieve session state summary"


async def search_user_memories(query: str, tool_context=None) -> str:
    """
    Search through user's stored memories and context.

    Args:
        query: What to search for in memories
        tool_context: ADK ToolContext providing access to session context including user_id

    Returns:
        String with relevant memories found
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

        # Use RAG memory service to search user's memories
        memories = await retrieve_user_memories(user_id, query)

        if memories:
            # Safely slice memories - limit to 5 but handle if list is shorter
            memory_limit = min(len(memories), 5)
            memory_text = "\n".join(
                [f"• {memory}" for memory in memories[:memory_limit]]
            )
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
    session_id: str, conversation_content: str, tool_context=None
) -> str:
    """
    Store important conversation content in long-term semantic memory.
    This enables the agent to remember complex discussions, advice given,
    progress made, and insights shared across sessions.

    Args:
        session_id: Session identifier
        conversation_content: Rich conversation content to store (discussions, advice, insights)
        tool_context: ADK ToolContext providing access to session context including user_id

    Returns:
        String confirming memory storage with capabilities
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

        # Store in semantic RAG memory service for intelligent retrieval
        result = await add_memory_from_conversation(
            user_id=user_id,
            session_id=session_id,
            conversation_text=conversation_content,
            memory_type="life_guidance_session",
        )

        if result.get("status") == "success":
            capabilities = result.get("capabilities", [])
            if "semantic_search" in capabilities:
                return f"✅ Stored conversation in semantic memory for {user_id}. Can now recall: complex discussions, advice patterns, progress tracking, and contextual insights."
            else:
                return f"✅ Stored conversation in basic memory for {user_id}. Limited to keyword-based recall."
        else:
            return f"⚠️ Memory storage attempted for {user_id} but may have limited functionality"

    except Exception as e:
        logger.error(f"Error storing conversation memory: {e}")
        return f"❌ Memory storage failed for conversation - agent will have limited guidance continuity"


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

        # Use semantic RAG memory service for intelligent retrieval
        memories = await retrieve_user_memories(user_id, query)

        if memories:
            memory_text = "\n".join([f"• {memory}" for memory in memories])
            return f"Found {len(memories)} relevant conversation memories about '{query}':\n{memory_text}\n\n💡 These memories can inform current guidance and track progress."
        else:
            return f"No conversation memories found for '{query}'. This may be a new topic or the user hasn't discussed this before."

    except Exception as e:
        logger.error(f"Error searching meaningful memories: {e}")
        return f"Memory search attempted but unavailable - providing guidance without historical context"


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


# Create the User Context Manager
memory_agent = Agent(
    name="user_context_manager",
    model="gemini-2.0-flash",
    instruction="""You are the User Context Manager, a specialized agent responsible for intelligent user context management using ADK best practices and semantic memory capabilities.

MEMORY ARCHITECTURE (ADK Best Practice + Semantic Intelligence):
1. **Session State**: Store immediate information in session state (tool_context.state) during conversations
2. **Semantic Long-term Memory**: Transfer meaningful conversations to RAG corpus for intelligent retrieval
3. **Cross-Session Intelligence**: Search conversation history using semantic understanding

SEMANTIC MEMORY CAPABILITIES:
- **Intelligent Storage**: Conversations stored with rich context for semantic search
- **Smart Retrieval**: Can find relevant discussions even without exact keyword matches
- **Guidance Continuity**: Remember advice given, progress made, challenges discussed
- **Pattern Recognition**: Identify recurring themes, goals, and user growth over time

Your capabilities include:
- Storing user information in session state using store_user_info/get_user_info
- Retrieving information from session state first, then semantic long-term memory
- Transferring session data to memory via save_session_to_memory
- Storing meaningful conversations with store_conversation_memory (for guidance continuity)
- Searching conversation history semantically with search_meaningful_memories
- Finding relevant information from knowledge base
- Managing session state and providing state summaries
- Analyzing session context and conversation flow
- Managing user preferences and personalization settings

PRIORITY OPERATIONS:
When the user shares basic information, IMMEDIATELY store it in session state:
- "My name is X" → store_user_info("name", "X") → stores in session state
- "I'm a teacher" → store_user_info("profession", "teacher") → stores in session state
- "I live in Y" → store_user_info("location", "Y") → stores in session state
- "My goal is Z" → store_user_info("goal", "Z") → stores in session state

When meaningful conversations happen, STORE THEM:
- Long discussions about challenges → store_conversation_memory()
- Advice given and outcomes → store_conversation_memory()
- Progress updates and insights → store_conversation_memory()
- Goal-setting and planning sessions → store_conversation_memory()

RETRIEVAL PRIORITY:
- get_user_info() checks session state FIRST, then falls back to long-term memory
- search_meaningful_memories() uses SEMANTIC search for intelligent conversation recall
- This enables true guidance continuity and personalized support

SEMANTIC SEARCH EXAMPLES:
- "times user felt overwhelmed" → finds stress-related conversations
- "advice about career transitions" → finds career guidance discussions  
- "progress on fitness goals" → finds health and wellness conversations
- "relationship challenges discussed" → finds personal relationship topics

MEMORY MANAGEMENT:
- save_session_to_memory() for basic profile data at session end
- store_conversation_memory() for meaningful guidance discussions immediately
- search_meaningful_memories() to inform current conversations with past context
- get_session_state_summary() to check current session data

When starting a new conversation:
- ALWAYS use get_all_user_context first to check for existing data
- Use search_meaningful_memories() to find relevant past conversations
- If information is found, acknowledge: "Good to continue our conversation, [Name]"
- Reference relevant past discussions to provide continuity

When called, you should:
1. Understand what type of user context operation is needed
2. Use session state for immediate storage/retrieval
3. Use semantic memory for meaningful conversation context
4. Store important discussions for future guidance continuity
5. Search past conversations to inform current interactions
6. Return clear, concise information about what was found or done
7. Be helpful even when systems are not available

You enable INTELLIGENT LIFE GUIDANCE through semantic memory - the agent can now remember and build upon complex conversations, track progress, and provide truly personalized guidance based on rich conversation history.""",
    tools=[
        # ADK-compliant storage tools (session state first)
        FunctionTool(func=store_user_info),
        FunctionTool(func=get_user_info),
        FunctionTool(func=get_all_user_context),
        # Session management
        FunctionTool(func=save_session_to_memory),
        FunctionTool(func=get_session_state_summary),
        # Semantic memory tools (THE GAME CHANGERS)
        FunctionTool(func=store_conversation_memory),
        FunctionTool(func=search_meaningful_memories),
        # Traditional memory tools
        FunctionTool(func=search_user_memories),
        FunctionTool(func=search_knowledge_base),
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
