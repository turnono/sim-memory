"""
Memory Service Configuration for Life Guidance

Simple configuration for ADK's built-in memory capabilities.
Since we use ADK's load_memory tool directly, most custom functions are not needed.
"""

import logging
import os
from typing import Dict, Any

from google.adk.memory import VertexAiRagMemoryService, InMemoryMemoryService

logger = logging.getLogger(__name__)

# Load environment variables
try:
    from dotenv import load_dotenv
    # Try loading from current directory first, then parent
    if os.path.exists('.env'):
        load_dotenv('.env')
    elif os.path.exists('../.env'):
        load_dotenv('../.env')
    elif os.path.exists('sim_guide/.env'):
        load_dotenv('sim_guide/.env')
except ImportError:
    # dotenv not available, environment should be set by Cloud Run
    pass

# Environment configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT")
LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION")
USE_VERTEX_AI_RAG = os.getenv("USE_VERTEX_AI_RAG", "true").lower() == "true"

# RAG Corpus configuration
RAG_CORPUS_RESOURCE_NAME = os.getenv(
    "RAG_CORPUS_RESOURCE_NAME",
    f"projects/{PROJECT_ID}/locations/{LOCATION}/ragCorpora/life-guidance-corpus"
)
SIMILARITY_TOP_K = int(os.getenv("SIMILARITY_TOP_K", "5"))
VECTOR_DISTANCE_THRESHOLD = float(os.getenv("VECTOR_DISTANCE_THRESHOLD", "0.7"))

def get_memory_service():
    """Get the configured memory service instance"""
    global _memory_service
    
    if '_memory_service' not in globals():
        if USE_VERTEX_AI_RAG and PROJECT_ID and LOCATION:
            try:
                # Initialize the memory service with Vertex AI RAG
                _memory_service = VertexAiRagMemoryService(
                    rag_corpus=RAG_CORPUS_RESOURCE_NAME,
                    similarity_top_k=SIMILARITY_TOP_K,
                    vector_distance_threshold=VECTOR_DISTANCE_THRESHOLD
                )
                logger.info("Using Vertex AI RAG memory service")
            except Exception as e:
                logger.warning(f"Failed to initialize Vertex AI RAG: {e}, falling back to in-memory")
                _memory_service = InMemoryMemoryService()
        else:
            # Use the simpler in-memory implementation for local testing
            _memory_service = InMemoryMemoryService()
            logger.info("Using in-memory memory service")
    
    return _memory_service

def get_memory_config() -> Dict[str, Any]:
    """Get memory service configuration details"""
    return {
        "use_vertex_ai_rag": USE_VERTEX_AI_RAG,
        "project_id": PROJECT_ID,
        "location": LOCATION,
        "corpus_name": RAG_CORPUS_RESOURCE_NAME,
        "similarity_top_k": SIMILARITY_TOP_K,
        "vector_distance_threshold": VECTOR_DISTANCE_THRESHOLD,
        "service_type": "VertexAiRagMemoryService" if USE_VERTEX_AI_RAG and PROJECT_ID else "InMemoryMemoryService"
    }
