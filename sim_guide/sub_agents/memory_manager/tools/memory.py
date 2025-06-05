"""
Enhanced Memory Tools for Life Guidance

Functions that leverage ADK memory capabilities and session state management
to provide better context and continuity for life guidance conversations.
"""

import logging
from google.adk.tools import load_memory, preload_memory, load_artifacts

logger = logging.getLogger(__name__)


def load_life_guidance_memory(query: str = "") -> str:
    """
    Load relevant memories and context for life guidance based on conversation history.

    Args:
        query: Specific query to search for in memories. If empty, uses general life guidance context.

    Returns:
        str: Status message indicating what memories were loaded or attempted to load.
    """
    try:
        # Build comprehensive memory query
        memory_query_parts = []

        # Base query from user input
        if query:
            memory_query_parts.append(query)

        # If no specific query, use general life guidance context
        if not memory_query_parts:
            memory_query_parts.append("life guidance personal context")

        final_query = " ".join(memory_query_parts)

        # Use ADK memory loading
        try:
            memory_result = load_memory(final_query)
            return f"Loaded relevant life guidance memories for: {final_query}"

        except Exception as mem_error:
            logger.debug(f"ADK load_memory failed: {mem_error}")
            return f"Memory search attempted for: {final_query} (no results found)"

    except Exception as e:
        logger.error(f"Error loading life guidance memory: {e}")
        return f"Error: Failed to load memory: {str(e)}"


def preload_life_context(context_type: str = "general") -> str:
    """
    Preload relevant context and resources for ongoing life guidance conversation.

    Args:
        context_type: Type of context to preload (general, career, relationships, health, etc.)

    Returns:
        str: Status message indicating what context was preloaded.
    """
    try:
        # Determine what context to preload
        preload_contexts = []

        if context_type == "general":
            preload_contexts = [
                "life guidance basics",
                "goal setting strategies",
                "personal development tips",
            ]
        elif context_type == "career":
            preload_contexts = [
                "career development guidance",
                "professional growth strategies",
                "workplace advice",
            ]
        elif context_type == "relationships":
            preload_contexts = [
                "relationship guidance",
                "communication skills",
                "social interaction tips",
            ]
        elif context_type == "health":
            preload_contexts = [
                "health and wellness guidance",
                "lifestyle optimization",
                "mental health support",
            ]
        else:
            preload_contexts = [f"{context_type} life guidance"]

        # Attempt to preload each context
        preloaded = []
        for context_query in preload_contexts:
            try:
                preload_memory(context_query)
                preloaded.append(context_query)
            except Exception as e:
                logger.debug(f"Preload failed for {context_query}: {e}")

        if preloaded:
            return f"Preloaded life guidance context: {', '.join(preloaded)}"
        else:
            return "No additional context available for preloading"

    except Exception as e:
        logger.error(f"Error preloading life context: {e}")
        return f"Error: Failed to preload context: {str(e)}"


def load_life_resources(resource_type: str = "general") -> str:
    """
    Load relevant life guidance resources and artifacts for specific life areas or challenges.

    Args:
        resource_type: Type of resources to load (career, relationships, health, finance, etc.)

    Returns:
        str: Status message indicating what resources were loaded.
    """
    try:
        # Map resource types to specific artifacts
        resource_map = {
            "career": ["resume templates", "interview guides", "career planning"],
            "relationships": [
                "communication guides",
                "relationship advice",
                "conflict resolution",
            ],
            "health": ["wellness plans", "fitness guides", "mental health resources"],
            "finance": [
                "budgeting templates",
                "investment guides",
                "financial planning",
            ],
            "personal_growth": [
                "self-improvement guides",
                "skill development",
                "learning resources",
            ],
            "productivity": [
                "time management",
                "organization systems",
                "productivity tools",
            ],
            "creativity": [
                "creative exercises",
                "inspiration guides",
                "artistic development",
            ],
            "social": ["networking guides", "social skills", "communication tips"],
            "spirituality": [
                "mindfulness guides",
                "purpose exploration",
                "meaning frameworks",
            ],
            "lifestyle": ["habit formation", "routine design", "life balance"],
            "general": ["life guidance", "goal setting", "personal development"],
        }

        # Get resources to load
        resources_to_load = resource_map.get(
            resource_type, ["life guidance", "goal setting"]
        )

        # Attempt to load artifacts
        loaded_resources = []
        for resource in resources_to_load[:5]:  # Limit to 5 resources max
            try:
                load_artifacts(resource)
                loaded_resources.append(resource)
            except Exception as e:
                logger.debug(f"Failed to load artifact {resource}: {e}")

        if loaded_resources:
            return f"Loaded life guidance resources: {', '.join(loaded_resources)}"
        else:
            return (
                f"Attempted to load resources for: {', '.join(resources_to_load[:3])}"
            )

    except Exception as e:
        logger.error(f"Error loading life resources: {e}")
        return f"Error: Failed to load resources: {str(e)}"
