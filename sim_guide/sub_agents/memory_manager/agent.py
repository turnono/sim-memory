"""
Memory Management Subagent

A specialized agent focused on memory management including:
memory operations and session management for the life guidance system.

This agent handles:
- Storing and retrieving user context in session state
- Loading memories using ADK's built-in memory service
- Session context analysis and management
- Conversation continuity tracking

Follows ADK patterns with tool_context and built-in memory services.
"""

import logging
from google.adk import Agent
from google.adk.tools import FunctionTool, load_memory

# Import prompts
from .prompt import DESCRIPTION, INSTRUCTION

# Import memory and session tools following ADK patterns
from .tools import (
    store_user_context,
    get_user_context,
    preload_life_context,
    load_life_resources,
    # Session tools
    analyze_session_context,
    get_conversation_continuity_hints,
    update_session_context,
    save_session_to_memory,
)

logger = logging.getLogger(__name__)


# === MEMORY AGENT CONFIGURATION ===

# Memory management tools following ADK patterns
memory_tools = [
    FunctionTool(func=store_user_context),
    FunctionTool(func=get_user_context),
    load_memory,  # ADK's built-in memory tool - handles VertexAI automatically
    FunctionTool(func=preload_life_context),
    FunctionTool(func=load_life_resources),
]

# Session management tools
session_tools = [
    FunctionTool(func=analyze_session_context),
    FunctionTool(func=get_conversation_continuity_hints),
    FunctionTool(func=update_session_context),
    FunctionTool(func=save_session_to_memory),
]

# Combine all memory management tools
all_memory_tools = memory_tools + session_tools

# Memory Management Agent
# Note: The memory service will be configured at the Runner level
memory_manager = Agent(
    name="memory_manager",
    model="gemini-2.0-flash",
    description=DESCRIPTION,
    instruction=INSTRUCTION,
    output_key="memory_operation_result",  # String key for memory operations
    tools=all_memory_tools,
)
