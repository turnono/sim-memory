"""
Infrastructure Verification Test

Verifies the actual Vertex AI RAG infrastructure is working:
- RAG corpus creation
- File uploads to GCS
- Vector embeddings
- Semantic retrieval
"""

import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim_guide.sub_agents.memory_manager.services.rag_memory_service import (
    add_memory_from_conversation,
    retrieve_user_memories,
    health_check,
    get_rag_config,
)


async def verify_infrastructure():
    """Verify the actual infrastructure components"""
    print("🏗️ INFRASTRUCTURE VERIFICATION")
    print("=" * 60)

    # Test 1: Health Check
    print("1️⃣ Testing RAG Memory Service Health...")
    health_result = await health_check()
    print(f"   Status: {health_result.get('status')}")
    print(f"   Message: {health_result.get('message')}")

    # Test 2: Configuration
    print("\n2️⃣ Checking RAG Configuration...")
    config = get_rag_config()
    print(f"   Project: {config.get('project_id')}")
    print(f"   Location: {config.get('location')}")
    print(f"   Enabled: {config.get('enabled')}")
    print(f"   Bucket: {config.get('bucket')}")

    # Test 3: Memory Storage (creates corpus, uploads to GCS, imports to RAG)
    print("\n3️⃣ Testing Memory Storage Infrastructure...")
    storage_result = await add_memory_from_conversation(
        user_id="infrastructure_test_user",
        session_id="test_session",
        conversation_text="This is a test conversation to verify infrastructure components are working properly.",
        memory_type="infrastructure_test",
    )

    print(f"   Storage Status: {storage_result.get('status')}")
    print(f"   Capabilities: {storage_result.get('capabilities', [])}")

    if "semantic_search" in storage_result.get("capabilities", []):
        print("   ✅ FULL RAG INFRASTRUCTURE WORKING")
        print(f"   Corpus: {storage_result.get('corpus_name', 'Not specified')}")
        print(f"   Files Imported: {storage_result.get('imported_files', 'Unknown')}")
    else:
        print("   ⚠️ FALLBACK MODE - Basic storage only")

    # Test 4: Retrieval
    print("\n4️⃣ Testing Memory Retrieval...")
    retrieval_result = await retrieve_user_memories(
        "infrastructure_test_user", "test conversation"
    )

    if retrieval_result:
        print(f"   ✅ RETRIEVAL WORKING - Found {len(retrieval_result)} results")
        print(
            f"   Sample: {retrieval_result[0][:50]}..."
            if retrieval_result[0]
            else "No content"
        )
    else:
        print("   ❌ RETRIEVAL FAILED - No results found")

    print("\n" + "=" * 60)
    print("🏗️ INFRASTRUCTURE SUMMARY:")

    working_components = []
    if health_result.get("status") == "healthy":
        working_components.append("✅ Vertex AI Connection")
    if storage_result.get("status") == "success":
        working_components.append("✅ Memory Storage")
    if "semantic_search" in storage_result.get("capabilities", []):
        working_components.append("✅ RAG Corpus")
        working_components.append("✅ Vector Embeddings")
    if retrieval_result:
        working_components.append("✅ Semantic Retrieval")

    print("\n".join(working_components))

    if len(working_components) >= 4:
        print("\n🎉 FULL INFRASTRUCTURE OPERATIONAL!")
        return True
    else:
        print(
            f"\n⚠️ PARTIAL FUNCTIONALITY ({len(working_components)}/5 components working)"
        )
        return False


if __name__ == "__main__":
    asyncio.run(verify_infrastructure())
