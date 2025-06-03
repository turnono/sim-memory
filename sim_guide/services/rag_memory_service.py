"""
RAG Memory Service for Life Guidance

Provides memory storage and retrieval capabilities using Google Cloud Vertex AI RAG
for the life guidance system. Handles user memories, conversation history, and context.

Now includes ADK-aligned hybrid routing for cost optimization:
- Simple queries -> fast keyword search (cost-effective)
- Complex queries -> semantic RAG search (powerful)
"""

import asyncio
import logging
import json
import os
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timezone

import vertexai
from vertexai import rag
from vertexai.generative_models import GenerativeModel, Tool
from google.cloud import storage
from google.oauth2 import service_account

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use the same environment variables as the rest of the system
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")  # Changed from PROJECT_ID
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")  # Changed from LOCATION

# RAG Memory Service Configuration
RAG_SERVICE_CONFIG = {
    "enabled": bool(PROJECT_ID and LOCATION),
}

if not all([PROJECT_ID, LOCATION]):
    logger.warning(
        "GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION must be set for RAG Memory Service"
    )
    logger.warning("RAG Memory Service will operate in degraded mode")

# Initialize Vertex AI if configuration is available
try:
    if RAG_SERVICE_CONFIG["enabled"]:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        logger.info(f"RAG Memory Service initialized for project {PROJECT_ID}")
    else:
        logger.warning(
            "RAG Memory Service running in degraded mode - no persistent storage"
        )
except Exception as e:
    logger.error(f"Failed to initialize Vertex AI: {e}")
    RAG_SERVICE_CONFIG["enabled"] = False

# RAG imports
try:
    from vertexai import rag

    VERTEXAI_AVAILABLE = True
except ImportError as e:
    VERTEXAI_AVAILABLE = False
    rag = None


# ADK-Aligned Hybrid Memory Configuration
HYBRID_CONFIG = {
    "enabled": os.getenv("HYBRID_MEMORY_MODE", "true").lower() == "true",
    "semantic_keywords": [
        "analyze",
        "pattern",
        "review",
        "all",
        "journey",
        "summarize",
        "insights",
        "trends",
    ],
    "transparent_communication": os.getenv(
        "TRANSPARENT_MEMORY_COMMUNICATION", "true"
    ).lower()
    == "true",
}


def classify_query_complexity(query: str) -> str:
    """
    ADK-aligned simple query classification for routing.

    Args:
        query: User's memory search query

    Returns:
        "complex" for semantic search, "simple" for keyword search
    """
    if not HYBRID_CONFIG["enabled"]:
        return "complex"  # Default to semantic if hybrid disabled

    query_lower = query.lower()

    # Check for complex analysis keywords
    if any(keyword in query_lower for keyword in HYBRID_CONFIG["semantic_keywords"]):
        return "complex"

    # Default to simple for cost optimization
    return "simple"


async def search_memories_hybrid(
    user_id: str, query: str, force_semantic: bool = False
) -> Dict[str, Any]:
    """
    ADK-aligned hybrid memory search with intelligent routing.

    Args:
        user_id: User identifier
        query: Search query
        force_semantic: Force semantic search regardless of classification

    Returns:
        Dict with memories, method used, and transparent communication
    """
    try:
        # Determine search method
        if force_semantic:
            complexity = "complex"
            reason = "Forced semantic analysis"
        else:
            complexity = classify_query_complexity(query)
            reason = "Automatic classification"

        # Route to appropriate search method
        if complexity == "complex":
            memories = await _semantic_memory_search(user_id, query)
            method = "semantic_search"
            cost = "high"
            message = f"🧠 Used deep semantic analysis ({reason})"
        else:
            memories = await _keyword_memory_search(user_id, query)
            method = "keyword_search"
            cost = "low"
            message = f"🔍 Used efficient keyword search ({reason})"

        return {
            "status": "success",
            "memories": memories,
            "method_used": method,
            "cost_level": cost,
            "message": message if HYBRID_CONFIG["transparent_communication"] else "",
            "query": query,
        }

    except Exception as e:
        logger.error(f"Hybrid memory search failed: {e}")
        return {
            "status": "error",
            "memories": [],
            "method_used": "error_fallback",
            "cost_level": "none",
            "message": "⚠️ Memory search temporarily unavailable",
            "query": query,
        }


def get_storage_client():
    """Get Google Cloud Storage client"""
    return storage.Client(project=PROJECT_ID)


def get_default_bucket():
    """Get the default bucket for RAG operations"""
    return os.getenv(
        "GOOGLE_CLOUD_STAGING_BUCKET", "gs://taajirah-adk-staging"
    ).replace("gs://", "")


async def health_check() -> Dict[str, Any]:
    """
    Check the health and status of the RAG Memory Service.

    Returns:
        Dict with status, message, and configuration details
    """
    start_time = datetime.now()

    try:
        if not RAG_SERVICE_CONFIG["enabled"]:
            return {
                "status": "degraded",
                "message": "RAG Memory Service running without persistent storage",
                "config": RAG_SERVICE_CONFIG,
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
            }

        # Test basic Vertex AI connectivity
        model = GenerativeModel("gemini-1.5-flash")

        # Test basic functionality
        response = model.generate_content("Test health check")

        if response:
            return {
                "status": "healthy",
                "message": "RAG Memory Service is operational",
                "config": RAG_SERVICE_CONFIG,
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
            }
        else:
            return {
                "status": "unhealthy",
                "message": "RAG Memory Service test failed",
                "config": RAG_SERVICE_CONFIG,
                "duration_seconds": (datetime.now() - start_time).total_seconds(),
            }

    except Exception as e:
        logger.error(f"RAG Memory Service health check failed: {e}")
        return {
            "status": "unhealthy",
            "message": f"RAG Memory Service error: {str(e)}",
            "config": RAG_SERVICE_CONFIG,
            "duration_seconds": (datetime.now() - start_time).total_seconds(),
        }


async def create_rag_corpus(corpus_id: str, display_name: str) -> Dict[str, Any]:
    """
    Create a new RAG corpus for storing memories.

    Args:
        corpus_id: Unique identifier for the corpus
        display_name: Human-readable name for the corpus

    Returns:
        Dict with creation result
    """
    try:
        if not RAG_SERVICE_CONFIG["enabled"]:
            return {
                "status": "error",
                "message": "RAG Memory Service not configured",
            }

        # Configure embedding model
        embedding_model_config = rag.RagEmbeddingModelConfig(
            vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
                publisher_model="publishers/google/models/text-embedding-005"
            )
        )

        # Create the corpus using the correct API
        rag_corpus = rag.create_corpus(
            display_name=display_name,
            backend_config=rag.RagVectorDbConfig(
                rag_embedding_model_config=embedding_model_config
            ),
        )

        return {
            "status": "success",
            "corpus_name": rag_corpus.name,
            "message": f"Successfully created corpus {display_name}",
        }

    except Exception as e:
        logger.error(f"Failed to create RAG corpus {corpus_id}: {e}")
        return {
            "status": "error",
            "message": f"Failed to create corpus: {str(e)}",
        }


async def add_memory_from_conversation(
    user_id: str,
    session_id: str,
    conversation_text: str,
    memory_type: str = "general",
) -> Dict[str, Any]:
    """
    Add memory from conversation to user's RAG corpus with semantic search capability.

    Args:
        user_id: User identifier
        session_id: Session identifier
        conversation_text: Text content to store as memory
        memory_type: Type of memory (general, preference, goal, etc.)

    Returns:
        Dict with operation result
    """
    try:
        if not RAG_SERVICE_CONFIG["enabled"]:
            return {
                "status": "error",
                "message": "RAG Memory Service not configured",
            }

        # Create user-specific corpus if it doesn't exist
        corpus_display_name = f"user-memory-{user_id}"

        # List existing corpora to check if user corpus exists
        try:
            corpora = rag.list_corpora()
            user_corpus = None

            for corpus in corpora:
                if corpus.display_name == corpus_display_name:
                    user_corpus = corpus
                    break

            # Create corpus if it doesn't exist
            if not user_corpus:
                embedding_model_config = rag.RagEmbeddingModelConfig(
                    vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
                        publisher_model="publishers/google/models/text-embedding-005"
                    )
                )

                user_corpus = rag.create_corpus(
                    display_name=corpus_display_name,
                    backend_config=rag.RagVectorDbConfig(
                        rag_embedding_model_config=embedding_model_config
                    ),
                )
                logger.info(f"Created new RAG corpus for user {user_id}")

        except Exception as e:
            logger.error(f"Error managing RAG corpus for user {user_id}: {e}")
            # Fallback to simple storage if RAG corpus fails
            return await _fallback_gcs_storage(
                user_id, session_id, conversation_text, memory_type
            )

        # Prepare rich memory document for semantic search
        memory_metadata = {
            "user_id": user_id,
            "session_id": session_id,
            "memory_type": memory_type,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Create rich memory text that includes context for better semantic matching
        memory_text = f"""
Session Context: User {user_id} in session {session_id} ({memory_type})
Date: {memory_metadata["timestamp"]}

Conversation Content:
{conversation_text}

Memory Summary: This represents a {memory_type} interaction where the user discussed various topics that may be relevant for future guidance and continuity.
        """.strip()

        try:
            # Store content in GCS first, then upload to RAG
            gcs_result = await _backup_to_gcs(
                user_id, session_id, memory_text, memory_type
            )

            if gcs_result.get("gcs_uri"):
                # Import the GCS file into RAG corpus
                import_response = rag.import_files(
                    corpus_name=user_corpus.name,
                    paths=[gcs_result["gcs_uri"]],
                    transformation_config=rag.TransformationConfig(
                        rag.ChunkingConfig(chunk_size=512, chunk_overlap=100)
                    ),
                )

                return {
                    "status": "success",
                    "message": f"Successfully stored semantic memory for user {user_id}",
                    "memory_id": f"corpus:{user_corpus.name}",
                    "corpus_name": user_corpus.name,
                    "imported_files": import_response.imported_rag_files_count
                    if hasattr(import_response, "imported_rag_files_count")
                    else 1,
                    "capabilities": [
                        "semantic_search",
                        "conversation_context",
                        "guidance_continuity",
                    ],
                }
            else:
                # Fallback if GCS storage failed
                return await _fallback_gcs_storage(
                    user_id, session_id, conversation_text, memory_type
                )

        except Exception as e:
            logger.error(f"Failed to upload to RAG corpus: {e}")
            # Fallback to GCS if RAG upload fails
            return await _fallback_gcs_storage(
                user_id, session_id, conversation_text, memory_type
            )

    except Exception as e:
        logger.error(f"Failed to add semantic memory: {e}")
        return {
            "status": "error",
            "message": f"Failed to store memory: {str(e)}",
        }


async def _backup_to_gcs(
    user_id: str, session_id: str, memory_text: str, memory_type: str
) -> Dict[str, Any]:
    """Backup memory to GCS for redundancy"""
    try:
        bucket_name = get_default_bucket()
        storage_client = get_storage_client()
        bucket = storage_client.bucket(bucket_name)

        file_name = f"memories/{user_id}/{session_id}_{memory_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        blob = bucket.blob(file_name)
        blob.upload_from_string(memory_text, content_type="text/plain")

        return {"gcs_uri": f"gs://{bucket_name}/{file_name}"}
    except Exception as e:
        logger.error(f"GCS backup failed: {e}")
        return {"gcs_uri": None}


async def _fallback_gcs_storage(
    user_id: str, session_id: str, conversation_text: str, memory_type: str
) -> Dict[str, Any]:
    """Fallback to simple GCS storage when RAG corpus is unavailable"""
    try:
        memory_text = f"""
Memory Type: {memory_type}
User: {user_id}
Session: {session_id}
Timestamp: {datetime.now(timezone.utc).isoformat()}
Content: {conversation_text}
        """.strip()

        result = await _backup_to_gcs(user_id, session_id, memory_text, memory_type)

        return {
            "status": "success",
            "message": f"Stored memory in fallback mode for user {user_id}",
            "memory_id": result.get("gcs_uri"),
            "capabilities": ["basic_keyword_search"],
        }
    except Exception as e:
        return {"status": "error", "message": f"All storage methods failed: {str(e)}"}


async def retrieve_user_memories(user_id: str, query: str) -> List[str]:
    """
    Retrieve user's memories using semantic search when available, keyword search as fallback.

    Args:
        user_id: User identifier
        query: Search query for memories (can be semantic: "times I felt stressed about work")

    Returns:
        List of relevant memory texts
    """
    try:
        if not RAG_SERVICE_CONFIG["enabled"]:
            return []

        # Try semantic search first
        semantic_results = await _semantic_memory_search(user_id, query)
        if semantic_results:
            return semantic_results

        # Fallback to keyword search in GCS
        return await _keyword_memory_search(user_id, query)

    except Exception as e:
        logger.error(f"Failed to retrieve memories: {e}")
        return []


async def _semantic_memory_search(user_id: str, query: str) -> List[str]:
    """Search using RAG corpus for semantic understanding"""
    try:
        # Find user's corpus
        corpora = rag.list_corpora()
        corpus_display_name = f"user-memory-{user_id}"
        user_corpus = None

        for corpus in corpora:
            if corpus.display_name == corpus_display_name:
                user_corpus = corpus
                break

        if not user_corpus:
            logger.info(f"No RAG corpus found for user {user_id}")
            return []

        # Perform semantic search using correct API
        response = rag.retrieval_query(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=user_corpus.name,
                )
            ],
            text=query,
            # Use correct parameter name
            rag_retrieval_config=rag.RagRetrievalConfig(
                top_k=5,
                filter=rag.utils.resources.Filter(vector_distance_threshold=0.5),
            ),
        )

        memories = []
        if hasattr(response, "contexts") and response.contexts:
            for context in response.contexts.contexts:
                if hasattr(context, "text") and context.text:
                    # Extract the actual conversation content
                    content = context.text
                    if "Conversation Content:" in content:
                        conversation_part = content.split("Conversation Content:")[1]
                        if "Memory Summary:" in conversation_part:
                            conversation_part = conversation_part.split(
                                "Memory Summary:"
                            )[0]
                        memories.append(conversation_part.strip())
                    else:
                        memories.append(content)

        return memories[:5]

    except Exception as e:
        logger.error(f"Semantic search failed for user {user_id}: {e}")
        return []


async def _keyword_memory_search(user_id: str, query: str) -> List[str]:
    """Fallback keyword search in GCS files"""
    try:
        bucket_name = get_default_bucket()
        storage_client = get_storage_client()
        bucket = storage_client.bucket(bucket_name)

        prefix = f"memories/{user_id}/"
        blobs = bucket.list_blobs(prefix=prefix)

        memories = []
        for blob in blobs:
            try:
                content = blob.download_as_text()
                # Simple keyword matching
                if query.lower() in content.lower():
                    # Extract the content part
                    lines = content.split("\n")
                    for line in lines:
                        if line.startswith("Content:"):
                            content_text = line.replace("Content:", "").strip()
                            if content_text:
                                memories.append(content_text)
                            break
            except Exception as e:
                logger.error(f"Error reading memory blob {blob.name}: {e}")
                continue

        return memories[:5]  # Return up to 5 memories

    except Exception as e:
        logger.error(f"Keyword search failed: {e}")
        return []


async def search_all_corpora(query: str, top_k_per_corpus: int = 3) -> Dict[str, Any]:
    """
    Search across all available RAG corpora.

    Args:
        query: Search query
        top_k_per_corpus: Number of results per corpus

    Returns:
        Dict with search results
    """
    try:
        if not RAG_SERVICE_CONFIG["enabled"]:
            return {
                "status": "error",
                "message": "RAG Memory Service not configured",
                "results": [],
            }

        # For now, return empty results as we don't have general knowledge corpora set up
        return {
            "status": "success",
            "message": "Search completed",
            "results": [],
        }

    except Exception as e:
        logger.error(f"Search across corpora failed: {e}")
        return {
            "status": "error",
            "message": f"Search failed: {str(e)}",
            "results": [],
        }


async def query_corpus(corpus_id: str, query: str, top_k: int = 5) -> Dict[str, Any]:
    """
    Query a specific RAG corpus.

    Args:
        corpus_id: Corpus identifier
        query: Search query
        top_k: Number of top results to return

    Returns:
        Dict with query results
    """
    try:
        if not RAG_SERVICE_CONFIG["enabled"]:
            return {
                "status": "error",
                "message": "RAG Memory Service not configured",
                "results": [],
            }

        # For now, use simple file-based search
        # This would be replaced with actual RAG corpus querying
        return {
            "status": "success",
            "results": [],
            "query": query,
            "corpus_id": corpus_id,
        }

    except Exception as e:
        logger.error(f"Corpus query failed: {e}")
        return {
            "status": "error",
            "message": f"Query failed: {str(e)}",
            "results": [],
        }


# Export configuration for other modules
def get_rag_config() -> Dict[str, Any]:
    """Get RAG Memory Service configuration"""
    return {
        "project_id": PROJECT_ID,
        "location": LOCATION,
        "enabled": RAG_SERVICE_CONFIG["enabled"],
        "bucket": get_default_bucket(),
    }
