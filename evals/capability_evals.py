"""
Capability Enhancement Evaluations

Tests that the agent has proper capability enhancement functionality:
1. Has capability_enhancement_manager as an AgentTool
2. System prompt includes capability enhancement instructions
3. Meta-cognitive capabilities are properly integrated
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim_guide.agent import root_agent


def test_capability_enhancement_agent_tool():
    """Test that the agent has the capability_enhancement_manager tool available"""
    # Check AgentTools for capability_enhancement_manager
    agent_tool_names = []
    for tool in root_agent.tools:
        if hasattr(tool, "agent") and hasattr(tool.agent, "name"):
            agent_tool_names.append(tool.agent.name)

    assert "capability_enhancement_manager" in agent_tool_names, (
        f"Agent should have capability_enhancement_manager tool. Available AgentTools: {agent_tool_names}"
    )

    print("✅ Agent has capability_enhancement_manager tool")


def test_meta_cognitive_instructions_in_prompt():
    """Test that the system prompt includes meta-cognitive capability instructions"""
    prompt = root_agent.instruction

    # Check for meta-cognitive integration
    assert "META-COGNITIVE INTEGRATION" in prompt, (
        "System prompt should include meta-cognitive integration section"
    )
    assert (
        "provide life guidance while recognizing and addressing your own limitations"
        in prompt
    ), "Should mention addressing own limitations"

    # Check for capability enhancement approach
    assert "CAPABILITY ENHANCEMENT APPROACH" in prompt, (
        "Should include capability enhancement approach"
    )
    assert "Natural Integration" in prompt, "Should emphasize natural integration"
    assert "User-Centric" in prompt, "Should emphasize user-centric improvements"

    print("✅ Meta-cognitive instructions properly included in prompt")


def test_when_to_suggest_improvements():
    """Test that prompt includes clear guidance on when to suggest improvements"""
    prompt = root_agent.instruction

    # Check for when to suggest improvements section
    assert "WHEN TO SUGGEST IMPROVEMENTS" in prompt, (
        "Should have section on when to suggest improvements"
    )
    assert "During Natural Conversation" in prompt, (
        "Should mention suggesting during natural conversation"
    )
    assert "After Recurring Patterns" in prompt, (
        "Should mention suggesting after recurring patterns"
    )
    assert "When Facing Limitations" in prompt, (
        "Should mention suggesting when facing limitations"
    )

    print("✅ Improvement suggestion guidelines properly included")


def test_capability_enhancement_examples():
    """Test that prompt includes concrete examples of capability enhancement"""
    prompt = root_agent.instruction

    # Check for enhancement examples
    assert "ENHANCEMENT EXAMPLES" in prompt, (
        "Should include enhancement examples section"
    )
    assert "Financial Struggles" in prompt, "Should include financial example"
    assert "Career Confusion" in prompt, "Should include career example"
    assert "Health Goals" in prompt, "Should include health example"
    assert "Business Decisions" in prompt, "Should include business example"

    print("✅ Capability enhancement examples properly included")


def test_specialized_managers_section():
    """Test that specialized managers are properly described"""
    prompt = root_agent.instruction

    # Check for specialized managers section
    assert "SPECIALIZED MANAGERS" in prompt, "Should have specialized managers section"
    assert "capability_enhancement_manager" in prompt, (
        "Should mention capability_enhancement_manager"
    )
    assert "analyzing gaps and designing system improvements" in prompt, (
        "Should describe capability enhancement purpose"
    )

    print("✅ Specialized managers properly described")


def test_agent_configuration():
    """Test basic agent configuration"""
    assert root_agent.name == "sim_guide", (
        f"Agent name should be 'sim_guide', got '{root_agent.name}'"
    )
    assert root_agent.model == "gemini-2.0-flash", (
        f"Agent should use gemini-2.0-flash model, got '{root_agent.model}'"
    )
    assert len(root_agent.tools) == 3, (
        f"Agent should have 3 tools, got {len(root_agent.tools)}"
    )

    print("✅ Agent configuration is correct")


def run_all_capability_tests():
    """Run all capability enhancement tests"""
    print("Running Capability Enhancement Evaluations...")
    print("=" * 50)

    test_capability_enhancement_agent_tool()
    test_meta_cognitive_instructions_in_prompt()
    test_when_to_suggest_improvements()
    test_capability_enhancement_examples()
    test_specialized_managers_section()
    test_agent_configuration()

    print("=" * 50)
    print("✅ All capability enhancement evaluations passed!")
    print("The agent has:")
    print("  - capability_enhancement_manager tool properly integrated")
    print("  - Meta-cognitive instructions in system prompt")
    print("  - Clear guidelines on when and how to suggest improvements")
    print("  - Concrete examples of capability enhancement scenarios")


if __name__ == "__main__":
    run_all_capability_tests()
