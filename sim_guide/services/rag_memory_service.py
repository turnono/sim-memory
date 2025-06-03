"""
RAG Memory Service for Life Guidance

Provides memory storage and retrieval capabilities using Google Cloud Vertex AI RAG
for the life guidance system. Handles user memories, conversation history, and context.
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

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Use the same environment variables as the rest of the system
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")  # Changed from PROJECT_ID
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")   # Changed from LOCATION

# RAG Memory Service Configuration
RAG_SERVICE_CONFIG = {
    "enabled": bool(PROJECT_ID and LOCATION),
}

if not all([PROJECT_ID, LOCATION]):
    logger.warning("GOOGLE_CLOUD_PROJECT and GOOGLE_CLOUD_LOCATION must be set for RAG Memory Service")
    logger.warning("RAG Memory Service will operate in degraded mode")

# Initialize Vertex AI if configuration is available
try:
    if RAG_SERVICE_CONFIG["enabled"]:
        vertexai.init(project=PROJECT_ID, location=LOCATION)
        logger.info(f"RAG Memory Service initialized for project {PROJECT_ID}")
    else:
        logger.warning("RAG Memory Service running in degraded mode - no persistent storage")
except Exception as e:
    logger.error(f"Failed to initialize Vertex AI: {e}")
    RAG_SERVICE_CONFIG["enabled"] = False


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
    Add memory from conversation to user's RAG corpus.

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
        
        # Try to create corpus (this will fail if it already exists, which is fine)
        try:
            corpus_result = await create_rag_corpus(user_id, corpus_display_name)
            if corpus_result["status"] == "error" and "already exists" not in corpus_result["message"]:
                return corpus_result
        except Exception:
            # Corpus might already exist, continue
            pass

        # Prepare memory document
        memory_content = {
            "user_id": user_id,
            "session_id": session_id,
            "memory_type": memory_type,
            "content": conversation_text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Convert to text format for RAG
        memory_text = f"""
Memory Type: {memory_type}
User: {user_id}
Session: {session_id}
Timestamp: {memory_content['timestamp']}
Content: {conversation_text}
        """.strip()

        # Store in Cloud Storage first
        bucket_name = get_default_bucket()
        storage_client = get_storage_client()
        bucket = storage_client.bucket(bucket_name)

        # Create unique file name
        file_name = f"memories/{user_id}/{session_id}_{memory_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        blob = bucket.blob(file_name)

        # Upload memory content
        blob.upload_from_string(memory_text, content_type="text/plain")

        gcs_uri = f"gs://{bucket_name}/{file_name}"

        # For now, we'll store the memory in GCS but won't import to RAG corpus
        # due to API complexity. We'll implement a simpler approach for retrieval.

        return {
            "status": "success",
            "message": f"Successfully stored memory for user {user_id}",
            "memory_id": file_name,
            "gcs_uri": gcs_uri,
        }

    except Exception as e:
        logger.error(f"Failed to add memory: {e}")
        return {
            "status": "error",
            "message": f"Failed to store memory: {str(e)}",
        }


async def retrieve_user_memories(user_id: str, query: str) -> List[str]:
    """
    Retrieve user's memories based on a query.

    Args:
        user_id: User identifier
        query: Search query for memories

    Returns:
        List of relevant memory texts
    """
    try:
        if not RAG_SERVICE_CONFIG["enabled"]:
            return []

        # For now, implement a simple file-based search
        # List files in user's memory directory
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
                    lines = content.split('\n')
                    for line in lines:
                        if line.startswith('Content:'):
                            content_text = line.replace('Content:', '').strip()
                            if content_text:
                                memories.append(content_text)
                            break
            except Exception as e:
                logger.error(f"Error reading memory blob {blob.name}: {e}")
                continue
                
        return memories[:5]  # Return up to 5 memories

    except Exception as e:
        logger.error(f"Failed to retrieve memories: {e}")
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
