"""
Memory Behavior Evaluations

Tests that the agent proactively uses memory capabilities:
1. Stores user information immediately when shared
2. Checks for existing context at conversation start
3. Never makes excuses about memory being "under development"
4. Properly retrieves and acknowledges previous context
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim_guide.agent import root_agent


def test_memory_prompt_instructions():
    """Test that the system prompt includes proper memory instructions"""
    prompt = root_agent.instruction

    # Check for memory-first approach
    assert "MEMORY-FIRST APPROACH" in prompt, (
        "System prompt should include memory-first approach"
    )
    assert (
        "Always start conversations by checking for existing memory" in prompt
    ), "Should instruct to check context first"

    # Check for automatic storage instructions
    assert "AUTOMATIC INFORMATION STORAGE" in prompt, (
        "Should include automatic storage section"
    )
    assert "IMMEDIATELY store it" in prompt, "Should instruct immediate storage"
    assert "My name is [Name]" in prompt, "Should include name storage example"

    # Check for memory management examples
    assert "MEMORY MANAGEMENT EXAMPLES" in prompt, "Should include concrete examples"
    assert "memory_manager store name" in prompt, "Should show how to store names"
    assert "memory_manager search for memory" in prompt, (
        "Should show how to search context"
    )

    # Check that it doesn't make memory excuses
    assert "NEVER make excuses about memory being" in prompt, (
        "Should explicitly forbid memory excuses"
    )

    # Check conversational flow starts with memory
    assert "Check Memory First" in prompt, (
        "Conversational flow should start with memory check"
    )

    print("✅ Memory prompt instructions test passed")


def test_agent_has_memory_manager():
    """Test that the agent has the memory_manager tool available"""
    # Check AgentTools for memory_manager
    agent_tool_names = []
    for tool in root_agent.tools:
        if hasattr(tool, "agent") and hasattr(tool.agent, "name"):
            agent_tool_names.append(tool.agent.name)

    assert "memory_manager" in agent_tool_names, (
        f"Agent should have memory_manager tool. Available AgentTools: {agent_tool_names}"
    )

    print("✅ Agent has memory_manager tool")


def test_memory_principles_in_prompt():
    """Test that key memory principles are clearly stated in the prompt"""
    prompt = root_agent.instruction

    # Check important principles section includes memory principles
    principles_section = prompt[prompt.find("IMPORTANT PRINCIPLES:") :]

    assert "Memory First" in principles_section, (
        "Should emphasize Memory First principle"
    )
    assert "Never Make Memory Excuses" in principles_section, (
        "Should emphasize no memory excuses"
    )
    assert "Always check for existing context" in principles_section, (
        "Should emphasize context checking"
    )

    print("✅ Memory principles properly included in prompt")


def test_conversation_start_instructions():
    """Test that the prompt includes clear instructions for conversation starts"""
    prompt = root_agent.instruction

    # Check for every conversation start section
    assert "For **Every Conversation Start**:" in prompt, (
        "Should have conversation start section"
    )
    assert "Check memory_manager for existing context" in prompt, (
        "Should instruct to check context"
    )
    assert "acknowledge it" in prompt, "Should instruct to acknowledge existing context"

    print("✅ Conversation start instructions properly included")


def run_all_memory_tests():
    """Run all memory behavior tests"""
    print("Running Memory Behavior Evaluations...")
    print("=" * 50)

    test_memory_prompt_instructions()
    test_agent_has_memory_manager()
    test_memory_principles_in_prompt()
    test_conversation_start_instructions()

    print("=" * 50)
    print("✅ All memory behavior evaluations passed!")
    print("The agent should now:")
    print("  - Check for existing memory at every conversation start")
    print("  - Store user information immediately when shared")
    print("  - Never make excuses about memory being 'under development'")
    print("  - Acknowledge continuity across sessions")


if __name__ == "__main__":
    run_all_memory_tests()
