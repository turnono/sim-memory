"""
RAG Memory Service Layer
Centralized RAG memory management for sim-memory application.
Provides business logic and clean abstractions over VertexAI RAG Engine.
"""

import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import vertexai
from vertexai import rag
from google.cloud import storage
import uuid
import mimetypes
import tempfile
import json

# Set up logging
logger = logging.getLogger(__name__)

# Configuration
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")

def _validate_environment():
    """Validate environment variables when needed"""
    if not all([PROJECT_ID, LOCATION]):
        raise ValueError("PROJECT_ID and LOCATION must be set for RAG Memory Service")

# Set up service account authentication
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "./taajirah-agents-service-account.json")

# Initialize Vertex AI lazily
def _init_vertexai():
    """Initialize Vertex AI when needed"""
    _validate_environment()
    vertexai.init(project=PROJECT_ID, location=LOCATION)

# Initialize GCS client lazily  
def _get_storage_client():
    """Get storage client when needed"""
    _validate_environment()
    return storage.Client(project=PROJECT_ID)

logger.info(f"RAG Memory service module loaded")

# RAG Configuration
RAG_DEFAULT_EMBEDDING_MODEL = "text-embedding-004"
RAG_DEFAULT_TOP_K = 10
RAG_DEFAULT_VECTOR_DISTANCE_THRESHOLD = 0.5

# Use existing staging bucket instead of creating new ones
RAG_STAGING_BUCKET = os.getenv("GOOGLE_CLOUD_STAGING_BUCKET", "gs://taajirah-adk-staging")
if RAG_STAGING_BUCKET.startswith("gs://"):
    RAG_BUCKET_NAME = RAG_STAGING_BUCKET[5:]  # Remove gs:// prefix
else:
    RAG_BUCKET_NAME = RAG_STAGING_BUCKET

logger.info(f"Using existing staging bucket for RAG: {RAG_STAGING_BUCKET}")

async def create_corpus(
    display_name: str,
    description: Optional[str] = None,
    embedding_model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a new RAG corpus in Vertex AI.
    
    Args:
        display_name: A human-readable name for the corpus
        description: Optional description for the corpus  
        embedding_model: The embedding model to use (default: text-embedding-004)
        
    Returns:
        Dict containing corpus details or error information
    """
    try:
        _init_vertexai()  # Initialize when needed
        
        if embedding_model is None:
            embedding_model = RAG_DEFAULT_EMBEDDING_MODEL
            
        # Configure embedding model using the correct API structure
        embedding_model_config = rag.RagEmbeddingModelConfig(
            vertex_prediction_endpoint=rag.VertexPredictionEndpoint(
                publisher_model=f"publishers/google/models/{embedding_model}"
            )
        )
        
        # Create the corpus with correct API structure
        rag_corpus = rag.create_corpus(
            display_name=display_name,
            description=description or f"RAG corpus for simulation guidance: {display_name}",
            backend_config=rag.RagVectorDbConfig(
                rag_embedding_model_config=embedding_model_config
            ),
        )
        
        # Extract corpus ID from the full name
        corpus_id = rag_corpus.name.split('/')[-1]
        
        logger.info(f"Created RAG corpus '{display_name}' with ID {corpus_id}")
        
        return {
            "status": "success",
            "corpus_name": rag_corpus.name,
            "corpus_id": corpus_id,
            "display_name": rag_corpus.display_name,
            "description": rag_corpus.description,
            "embedding_model": embedding_model,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to create RAG corpus '{display_name}': {e}")
        return {
            "status": "error",
            "error_message": str(e),
            "display_name": display_name
        }

async def list_corpora() -> Dict[str, Any]:
    """
    List all RAG corpora in the project.
    
    Returns:
        Dict containing list of corpora or error information
    """
    try:
        corpora = rag.list_corpora()
        
        corpus_list = []
        for corpus in corpora:
            corpus_id = corpus.name.split('/')[-1]
            corpus_list.append({
                "corpus_id": corpus_id,
                "corpus_name": corpus.name,
                "display_name": corpus.display_name,
                "description": corpus.description
            })
        
        logger.debug(f"Found {len(corpus_list)} RAG corpora")
        
        return {
            "status": "success",
            "corpora": corpus_list,
            "count": len(corpus_list)
        }
        
    except Exception as e:
        logger.error(f"Failed to list RAG corpora: {e}")
        return {
            "status": "error",
            "error_message": str(e),
            "corpora": []
        }

async def get_corpus(corpus_id: str) -> Dict[str, Any]:
    """
    Get details of a specific RAG corpus.
    
    Args:
        corpus_id: The ID of the corpus to retrieve
        
    Returns:
        Dict containing corpus details or error information
    """
    try:
        corpus_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragCorpora/{corpus_id}"
        corpus = rag.get_corpus(name=corpus_name)
        
        return {
            "status": "success",
            "corpus_id": corpus_id,
            "corpus_name": corpus.name,
            "display_name": corpus.display_name,
            "description": corpus.description
        }
        
    except Exception as e:
        logger.error(f"Failed to get RAG corpus {corpus_id}: {e}")
        return {
            "status": "error",
            "error_message": str(e),
            "corpus_id": corpus_id
        }

async def delete_corpus(corpus_id: str) -> Dict[str, Any]:
    """
    Delete a RAG corpus.
    
    Args:
        corpus_id: The ID of the corpus to delete
        
    Returns:
        Dict containing success/error status
    """
    try:
        corpus_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragCorpora/{corpus_id}"
        rag.delete_corpus(name=corpus_name)
        
        logger.info(f"Deleted RAG corpus {corpus_id}")
        
        return {
            "status": "success",
            "corpus_id": corpus_id,
            "message": f"Successfully deleted corpus {corpus_id}"
        }
        
    except Exception as e:
        logger.error(f"Failed to delete RAG corpus {corpus_id}: {e}")
        return {
            "status": "error",
            "error_message": str(e),
            "corpus_id": corpus_id
        }

async def upload_document_to_gcs(
    file_content: bytes,
    file_name: str,
    content_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Upload a document to the existing Google Cloud Storage staging bucket.
    
    Args:
        file_content: The file content as bytes
        file_name: The name for the file
        content_type: MIME type of the file
        
    Returns:
        Dict containing upload status and GCS URI
    """
    try:
        # Use existing staging bucket
        bucket = _get_storage_client().bucket(RAG_BUCKET_NAME)
        
        # Create a unique file path within the bucket
        file_path = f"rag-documents/{file_name}"
        blob = bucket.blob(file_path)
        
        # Set content type if provided
        if content_type:
            blob.content_type = content_type
        elif file_name:
            blob.content_type = mimetypes.guess_type(file_name)[0] or 'application/octet-stream'
        
        # Upload the file
        blob.upload_from_string(file_content)
        
        gcs_uri = f"gs://{RAG_BUCKET_NAME}/{file_path}"
        
        logger.info(f"Document uploaded to existing staging bucket: {gcs_uri}")
        
        return {
            "status": "success",
            "gcs_uri": gcs_uri,
            "bucket_name": RAG_BUCKET_NAME,
            "file_path": file_path,
            "size_bytes": len(file_content)
        }
        
    except Exception as e:
        logger.error(f"Failed to upload document to GCS: {e}")
        return {
            "status": "error",
            "error": str(e)
        }

async def import_document_to_corpus(
    corpus_id: str,
    gcs_uri: str,
    display_name: Optional[str] = None
) -> Dict[str, Any]:
    """
    Import a document from GCS into a RAG corpus.
    
    Args:
        corpus_id: The ID of the target corpus
        gcs_uri: The GCS URI of the document to import
        display_name: Optional display name for the document
        
    Returns:
        Dict containing import status and details
    """
    try:
        corpus_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragCorpora/{corpus_id}"
        
        # Import files using the correct API structure
        response = rag.import_files(
            corpus_name=corpus_name,
            paths=[gcs_uri],
            transformation_config=rag.TransformationConfig(
                chunking_config=rag.ChunkingConfig(
                    chunk_size=512,
                    chunk_overlap=100,
                ),
            ),
            max_embedding_requests_per_min=1000,
        )
        
        logger.info(f"Started import of document {gcs_uri} to corpus {corpus_id}")
        
        return {
            "status": "success",
            "corpus_id": corpus_id,
            "gcs_uri": gcs_uri,
            "display_name": display_name or gcs_uri.split('/')[-1],
            "imported_files_count": response.imported_rag_files_count if hasattr(response, 'imported_rag_files_count') else 1,
            "import_started_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to import document {gcs_uri} to corpus {corpus_id}: {e}")
        return {
            "status": "error",
            "error_message": str(e),
            "corpus_id": corpus_id,
            "gcs_uri": gcs_uri
        }

async def query_corpus(
    corpus_id: str,
    query: str,
    top_k: Optional[int] = None,
    vector_distance_threshold: Optional[float] = None
) -> Dict[str, Any]:
    """
    Query a specific RAG corpus for relevant documents.
    
    Args:
        corpus_id: The ID of the corpus to query
        query: The search query text
        top_k: Number of top results to return (default: 10)
        vector_distance_threshold: Minimum similarity threshold (default: 0.5)
        
    Returns:
        Dict containing search results or error information
    """
    try:
        if top_k is None:
            top_k = RAG_DEFAULT_TOP_K
        if vector_distance_threshold is None:
            vector_distance_threshold = RAG_DEFAULT_VECTOR_DISTANCE_THRESHOLD
            
        corpus_name = f"projects/{PROJECT_ID}/locations/{LOCATION}/ragCorpora/{corpus_id}"
        
        # Configure retrieval settings
        rag_retrieval_config = rag.RagRetrievalConfig(
            top_k=top_k,
            filter=rag.Filter(vector_distance_threshold=vector_distance_threshold),
        )
        
        # Query the corpus using the correct API structure
        response = rag.retrieval_query(
            rag_resources=[
                rag.RagResource(
                    rag_corpus=corpus_name,
                )
            ],
            text=query,
            rag_retrieval_config=rag_retrieval_config,
        )
        
        logger.debug(f"Queried corpus {corpus_id} for: '{query[:50]}...'")
        
        # Process and format results
        results = []
        if hasattr(response, 'contexts') and response.contexts:
            for context in response.contexts.contexts:
                results.append({
                    "text": context.text,
                    "source": context.source_uri if hasattr(context, 'source_uri') else None,
                    "distance": context.distance if hasattr(context, 'distance') else None
                })
        
        return {
            "status": "success",
            "corpus_id": corpus_id,
            "query": query,
            "results": results,
            "results_count": len(results),
            "top_k": top_k,
            "vector_distance_threshold": vector_distance_threshold,
            "queried_at": datetime.now(timezone.utc).isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to query corpus {corpus_id}: {e}")
        return {
            "status": "error",
            "error_message": str(e),
            "corpus_id": corpus_id,
            "query": query
        }

async def search_all_corpora(
    query: str,
    top_k_per_corpus: Optional[int] = None
) -> Dict[str, Any]:
    """
    Search across all available RAG corpora.
    
    Args:
        query: The search query
        top_k_per_corpus: Number of results to return per corpus
        
    Returns:
        Dict containing aggregated search results
    """
    try:
        if top_k_per_corpus is None:
            top_k_per_corpus = 5  # Fewer per corpus when searching all
            
        # Get all corpora
        corpora_response = await list_corpora()
        if corpora_response["status"] != "success":
            return corpora_response
            
        all_results = []
        corpus_summaries = []
        
        for corpus_info in corpora_response["corpora"]:
            corpus_id = corpus_info["corpus_id"]
            
            # Query each corpus
            corpus_results = await query_corpus(
                corpus_id=corpus_id,
                query=query,
                top_k=top_k_per_corpus
            )
            
            if corpus_results["status"] == "success" and corpus_results["results"]:
                # Add corpus context to results
                for result in corpus_results["results"]:
                    result["corpus_id"] = corpus_id
                    result["corpus_name"] = corpus_info["display_name"]
                    all_results.append(result)
                
                corpus_summaries.append({
                    "corpus_id": corpus_id,
                    "corpus_name": corpus_info["display_name"],
                    "result_count": len(corpus_results["results"])
                })
        
        logger.info(f"Search across all corpora returned {len(all_results)} total results")
        
        return {
            "status": "success",
            "query": query,
            "results": all_results,
            "total_results": len(all_results),
            "corpus_summaries": corpus_summaries,
            "searched_corpora_count": len(corpora_response["corpora"])
        }
        
    except Exception as e:
        logger.error(f"Failed to search all corpora: {e}")
        return {
            "status": "error",
            "error_message": str(e),
            "query": query
        }

async def add_memory_from_conversation(
    user_id: str,
    session_id: str,
    conversation_text: str,
    memory_type: str = "conversation"
) -> Dict[str, Any]:
    """
    Add conversation memory to a dedicated RAG corpus for long-term memory.
    
    Args:
        user_id: User identifier
        session_id: Session identifier
        conversation_text: The conversation content to store
        memory_type: Type of memory (conversation, simulation_result, etc.)
        
    Returns:
        Dict containing memory storage results
    """
    try:
        # Create or get user-specific corpus
        corpus_name = f"user-memory-{user_id}"
        corpus_id = None
        
        # Check if user corpus exists
        corpora_response = await list_corpora()
        if corpora_response["status"] == "success":
            for corpus in corpora_response["corpora"]:
                if corpus["display_name"] == corpus_name:
                    corpus_id = corpus["corpus_id"]
                    break
        
        # Create corpus if it doesn't exist
        if corpus_id is None:
            corpus_response = await create_corpus(
                display_name=corpus_name,
                description=f"Long-term memory corpus for user {user_id}",
                embedding_model=RAG_DEFAULT_EMBEDDING_MODEL
            )
            
            if corpus_response["status"] != "success":
                return corpus_response
                
            corpus_id = corpus_response["corpus_id"]
        
        # Create memory document
        memory_doc = {
            "user_id": user_id,
            "session_id": session_id,
            "memory_type": memory_type,
            "content": conversation_text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "metadata": {
                "source": "sim_guide_session",
                "version": "1.0"
            }
        }
        
        # Create text content for RAG
        memory_text = f"""
User: {user_id}
Session: {session_id}
Type: {memory_type}
Timestamp: {memory_doc['timestamp']}

Content:
{conversation_text}
"""
        
        # Upload to GCS
        filename = f"memory_{user_id}_{session_id}_{int(datetime.now().timestamp())}.txt"
        upload_response = await upload_document_to_gcs(
            file_content=memory_text.encode('utf-8'),
            file_name=filename,
            content_type="text/plain"
        )
        
        if upload_response["status"] != "success":
            return upload_response
        
        # Import to corpus
        import_response = await import_document_to_corpus(
            corpus_id=corpus_id,
            gcs_uri=upload_response["gcs_uri"],
            display_name=f"Memory: {memory_type} from {session_id}"
        )
        
        if import_response["status"] != "success":
            return import_response
        
        logger.info(f"Added memory for user {user_id}, session {session_id}")
        
        return {
            "status": "success",
            "user_id": user_id,
            "session_id": session_id,
            "corpus_id": corpus_id,
            "memory_type": memory_type,
            "gcs_uri": upload_response["gcs_uri"],
            "timestamp": memory_doc["timestamp"]
        }
        
    except Exception as e:
        logger.error(f"Failed to add memory for user {user_id}: {e}")
        return {
            "status": "error",
            "error_message": str(e),
            "user_id": user_id,
            "session_id": session_id
        }

async def retrieve_user_memories(
    user_id: str,
    query: str,
    top_k: Optional[int] = None
) -> Dict[str, Any]:
    """
    Retrieve relevant memories for a user based on a query.
    
    Args:
        user_id: User identifier
        query: Query to find relevant memories
        top_k: Number of memories to return
        
    Returns:
        Dict containing relevant memories
    """
    try:
        if top_k is None:
            top_k = 5
            
        # Find user corpus
        corpus_name = f"user-memory-{user_id}"
        corpus_id = None
        
        corpora_response = await list_corpora()
        if corpora_response["status"] == "success":
            for corpus in corpora_response["corpora"]:
                if corpus["display_name"] == corpus_name:
                    corpus_id = corpus["corpus_id"]
                    break
        
        if corpus_id is None:
            return {
                "status": "success",
                "user_id": user_id,
                "memories": [],
                "message": f"No memory corpus found for user {user_id}"
            }
        
        # Query user's memory corpus
        query_response = await query_corpus(
            corpus_id=corpus_id,
            query=query,
            top_k=top_k
        )
        
        if query_response["status"] != "success":
            return query_response
        
        logger.debug(f"Retrieved {len(query_response['results'])} memories for user {user_id}")
        
        return {
            "status": "success",
            "user_id": user_id,
            "query": query,
            "memories": query_response["results"],
            "memory_count": len(query_response["results"])
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve memories for user {user_id}: {e}")
        return {
            "status": "error",
            "error_message": str(e),
            "user_id": user_id,
            "query": query
        }

async def health_check() -> Dict[str, Any]:
    """
    Perform health check on the RAG memory service.
    
    Returns:
        Dict containing health status
    """
    try:
        start_time = datetime.now(timezone.utc)
        
        # Test corpus listing
        corpora_response = await list_corpora()
        
        # Test basic functionality
        test_successful = corpora_response["status"] == "success"
        
        end_time = datetime.now(timezone.utc)
        duration = (end_time - start_time).total_seconds()
        
        return {
            "status": "healthy" if test_successful else "degraded",
            "duration_seconds": duration,
            "timestamp": end_time.isoformat(),
            "corpora_accessible": test_successful,
            "corpora_count": len(corpora_response.get("corpora", [])),
            "project_id": PROJECT_ID,
            "location": LOCATION
        }
        
    except Exception as e:
        logger.error(f"RAG memory service health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat()
        } 



       
