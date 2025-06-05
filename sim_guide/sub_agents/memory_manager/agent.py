"""
Memory Management Subagent

A specialized agent focused on memory management including:
memory operations and session management for the life guidance system.

This agent handles:
- Loading and searching memories with ADK-aligned hybrid routing
- Managing RAG corpus operations
- Context preloading and optimization
- Memory storage and retrieval
- Cross-session memory continuity
- Session context analysis and management
- Conversation continuity tracking

User preferences are now handled naturally by the LLM and RAG memory system.
"""

import logging
from google.adk import Agent
from google.adk.tools import FunctionTool

# Import prompts
from .prompt import DESCRIPTION, INSTRUCTION

# Import memory tools
from .tools import (
    load_life_guidance_memory,
    preload_life_context,
    load_life_resources,
    # Session tools
    analyze_session_context,
    get_conversation_continuity_hints,
    update_session_context,
)

logger = logging.getLogger(__name__)


# === MEMORY AGENT CONFIGURATION ===

# Memory management tools
memory_tools = [
    FunctionTool(func=load_life_guidance_memory),
    FunctionTool(func=preload_life_context),
    FunctionTool(func=load_life_resources),
]

# Session management tools
session_tools = [
    FunctionTool(func=analyze_session_context),
    FunctionTool(func=get_conversation_continuity_hints),
    FunctionTool(func=update_session_context),
]

# Combine all memory management tools
all_memory_tools = memory_tools + session_tools

# Memory Management Agent
memory_manager = Agent(
    name="memory_manager",
    model="gemini-2.0-flash",
    description=DESCRIPTION,
    instruction=INSTRUCTION,
    output_key="memory_search_result",  # String key for memory operations
    tools=all_memory_tools,
)
