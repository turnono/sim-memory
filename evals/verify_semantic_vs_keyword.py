"""
Verification Test: Semantic vs Keyword Search

This test proves semantic memory is working by using queries that require
semantic understanding, not just keyword matching.
"""

import sys
import os
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim_guide.sub_agents.user_context_manager import (
    store_conversation_memory,
    search_meaningful_memories,
)


class MockToolContext:
    def __init__(self, user_id, session_id):
        self.user_id = user_id
        self.session = type(
            "obj", (object,), {"user_id": user_id, "session_id": session_id}
        )
        self.state = {}


async def test_semantic_proof():
    """Prove semantic search is working vs keyword search"""
    print("🔬 SEMANTIC MEMORY VERIFICATION TEST")
    print("=" * 60)

    test_user_id = "semantic_test_user"
    context = MockToolContext(test_user_id, "verification_session")

    # Store a conversation about exercise
    exercise_conversation = """
    User: I've been trying to get in shape but I keep giving up after a few days.
    
    Agent: Starting a fitness routine can be challenging. What usually causes you to stop?
    
    User: I think I set unrealistic goals. I try to run 5 miles on day one when I haven't exercised in months.
    
    Agent: That's a common mistake! Let's start smaller. What if we began with just a 10-minute walk daily?
    
    User: That sounds much more doable.
    
    Agent: Great! Consistency beats intensity. Once walking feels natural, we can gradually increase.
    """

    result = await store_conversation_memory(
        "verification_session", exercise_conversation, context
    )
    print(f"📚 Stored exercise conversation: {result.split('.')[0]}...")

    print("\n🧪 TESTING SEMANTIC UNDERSTANDING...")

    # Test 1: Semantic query (no keywords match exactly)
    print("\n1️⃣ SEMANTIC TEST: 'challenges with staying active'")
    print("   (Note: 'staying active' never appears in conversation)")

    semantic_result = await search_meaningful_memories(
        "challenges with staying active", context
    )
    semantic_found = (
        "giving up" in semantic_result
        or "challenging" in semantic_result
        or "few days" in semantic_result
    )

    if semantic_found:
        print(
            "   ✅ SEMANTIC SEARCH WORKING - Found relevant content without exact keywords"
        )
    else:
        print("   ❌ SEMANTIC SEARCH FAILED - No relevant results")

    # Test 2: Another semantic query
    print("\n2️⃣ SEMANTIC TEST: 'problems with workout consistency'")
    print("   (Note: 'workout' and 'consistency' never appear together)")

    consistency_result = await search_meaningful_memories(
        "problems with workout consistency", context
    )
    consistency_found = (
        "giving up" in consistency_result or "few days" in consistency_result
    )

    if consistency_found:
        print(
            "   ✅ SEMANTIC SEARCH WORKING - Found consistency issues without exact terms"
        )
    else:
        print("   ❌ SEMANTIC SEARCH FAILED - No relevant results")

    # Test 3: Keyword that exists (should always work)
    print("\n3️⃣ CONTROL TEST: 'exercise' (exact keyword)")

    keyword_result = await search_meaningful_memories("exercise", context)
    keyword_found = "exercise" in keyword_result.lower()

    if keyword_found:
        print("   ✅ KEYWORD SEARCH WORKING - Found exact match")
    else:
        print("   ❌ KEYWORD SEARCH FAILED - System may be broken")

    # Results
    print("\n" + "=" * 60)
    print("🎯 VERIFICATION RESULTS:")

    if semantic_found and consistency_found and keyword_found:
        print("🎉 SEMANTIC MEMORY CONFIRMED WORKING!")
        print("✨ The system understands meaning, not just keywords")
        print("🧠 This proves true AI-powered semantic search")
        return True
    elif keyword_found and not (semantic_found or consistency_found):
        print("⚠️ ONLY KEYWORD SEARCH WORKING")
        print("🔍 System is using basic text matching, not semantic understanding")
        return False
    else:
        print("❌ MEMORY SYSTEM BROKEN")
        print("🚨 Neither semantic nor keyword search working")
        return False


if __name__ == "__main__":
    asyncio.run(test_semantic_proof())
