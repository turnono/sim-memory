#!/usr/bin/env python3
"""
Meta-Cognitive Capabilities Evaluation

Tests the meta-cognitive agent's ability to analyze its own capabilities,
suggest improvements, and design enhanced sub-agents and tools.
"""

import asyncio
import sys
import os
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim_guide.sub_agents.capability_enhancement_agent import (
    capability_enhancement_agent,
    analyze_capability_gaps,
    suggest_new_subagents,
    recommend_mcp_tools,
    design_user_clone_agent,
    prioritize_system_improvements,
    generate_capability_implementation_plan,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_capability_gap_analysis():
    """Test capability gap analysis functionality"""
    print("\n🔍 Testing Capability Gap Analysis")
    print("-" * 50)

    try:
        user_query = "I'm struggling to balance my startup work, personal relationships, and learning new skills. I feel overwhelmed and need a system to manage it all."
        user_context = "Software engineer, 28 years old, working on a side startup while maintaining a full-time job. Recently moved to a new city and trying to build social connections."
        current_capabilities = "Basic life guidance, memory management, general advice"

        result = await analyze_capability_gaps(
            user_query, user_context, current_capabilities
        )

        # Basic validation
        assert "CAPABILITY GAP ANALYSIS" in result
        assert "IDENTIFIED GAPS" in result
        assert "RECOMMENDED ENHANCEMENTS" in result

        print("✅ Capability gap analysis working correctly")
        return True

    except Exception as e:
        print(f"❌ Capability gap analysis failed: {e}")
        return False


async def test_subagent_suggestions():
    """Test sub-agent suggestion functionality"""
    print("\n🤖 Testing Sub-Agent Suggestions")
    print("-" * 50)

    try:
        user_profile = "Ambitious entrepreneur with technical background, values efficiency and growth, prefers data-driven decisions"
        recurring_needs = "Time management, decision-making frameworks, networking strategies, skill development planning"
        expertise_gaps = (
            "Business strategy, sales, marketing, leadership, financial planning"
        )

        result = await suggest_new_subagents(
            user_profile, recurring_needs, expertise_gaps
        )

        # Basic validation
        assert "SUGGESTED NEW SUB-AGENTS" in result
        assert "DOMAIN EXPERT AGENTS" in result
        assert "USER-SPECIFIC CLONE AGENTS" in result
        assert "WORKFLOW AUTOMATION AGENTS" in result

        print("✅ Sub-agent suggestions working correctly")
        return True

    except Exception as e:
        print(f"❌ Sub-agent suggestions failed: {e}")
        return False


async def test_mcp_tool_recommendations():
    """Test MCP tool recommendation functionality"""
    print("\n🔧 Testing MCP Tool Recommendations")
    print("-" * 50)

    try:
        user_challenges = "Information overload, scattered productivity tools, manual tracking of habits and goals"
        workflow_analysis = "Uses multiple apps without integration, spends time on repetitive tasks, lacks automated insights"

        result = await recommend_mcp_tools(user_challenges, workflow_analysis)

        # Basic validation
        assert "MCP TOOL RECOMMENDATIONS" in result
        assert "ESSENTIAL MCP TOOLS" in result
        assert "PRODUCTIVITY TOOLS" in result
        assert "IMPLEMENTATION PRIORITY" in result

        print("✅ MCP tool recommendations working correctly")
        return True

    except Exception as e:
        print(f"❌ MCP tool recommendations failed: {e}")
        return False


async def test_clone_agent_design():
    """Test user clone agent design functionality"""
    print("\n🧬 Testing User Clone Agent Design")
    print("-" * 50)

    try:
        user_personality = "Analytical, detail-oriented, values authenticity, prefers direct communication, risk-aware but willing to take calculated risks"
        specialized_role = "Business Strategist"
        expertise_domain = (
            "MBA-level business strategy, market analysis, competitive intelligence"
        )

        result = await design_user_clone_agent(
            user_personality, specialized_role, expertise_domain
        )

        # Basic validation
        assert "USER CLONE AGENT DESIGN" in result
        assert "PERSONALITY FOUNDATION" in result
        assert "SPECIALIZED EXPERTISE" in result
        assert "CAPABILITIES" in result
        assert "IMPLEMENTATION" in result

        print("✅ User clone agent design working correctly")
        return True

    except Exception as e:
        print(f"❌ User clone agent design failed: {e}")
        return False


async def test_system_improvement_prioritization():
    """Test system improvement prioritization functionality"""
    print("\n📈 Testing System Improvement Prioritization")
    print("-" * 50)

    try:
        user_goals = "Launch successful startup, maintain work-life balance, build strong professional network"
        current_pain_points = (
            "Time management, decision paralysis, lack of business expertise, isolation"
        )
        available_resources = (
            "Technical skills, limited time for setup, moderate budget for tools"
        )

        result = await prioritize_system_improvements(
            user_goals, current_pain_points, available_resources
        )

        # Basic validation
        assert "SYSTEM IMPROVEMENT ROADMAP" in result
        assert "PHASE 1: IMMEDIATE IMPACT" in result
        assert "PHASE 2: WORKFLOW OPTIMIZATION" in result
        assert "IMPLEMENTATION STRATEGY" in result

        print("✅ System improvement prioritization working correctly")
        return True

    except Exception as e:
        print(f"❌ System improvement prioritization failed: {e}")
        return False


async def test_implementation_plan_generation():
    """Test implementation plan generation functionality"""
    print("\n📋 Testing Implementation Plan Generation")
    print("-" * 50)

    try:
        selected_improvements = "Business strategy clone agent, calendar integration, task management MCP tools"
        user_preferences = "Gradual implementation, test before full deployment, minimize disruption to current workflow"
        timeline = "2 months with weekly milestones"

        result = await generate_capability_implementation_plan(
            selected_improvements, user_preferences, timeline
        )

        # Basic validation
        assert "IMPLEMENTATION PLAN" in result
        assert "DETAILED STEPS" in result
        assert "WEEK 1: FOUNDATION SETUP" in result
        assert "SUCCESS METRICS" in result
        assert "NEXT STEPS" in result

        print("✅ Implementation plan generation working correctly")
        return True

    except Exception as e:
        print(f"❌ Implementation plan generation failed: {e}")
        return False


async def test_agent_integration():
    """Test that the capability enhancement agent is properly integrated with the main agent"""
    print("\n🔗 Testing Agent Integration")
    print("-" * 50)

    try:
        from sim_guide.agent import root_agent

        # Check that capability enhancement agent is included in tools
        agent_tools = [
            tool.agent.name for tool in root_agent.tools if hasattr(tool, "agent")
        ]
        assert "capability_enhancement_manager" in agent_tools

        print("✅ Capability enhancement agent properly integrated with main agent")
        return True

    except Exception as e:
        print(f"❌ Agent integration test failed: {e}")
        return False


async def run_all_meta_cognitive_tests():
    """Run all meta-cognitive capability tests"""
    print("🚀 META-COGNITIVE CAPABILITIES EVALUATION")
    print("=" * 60)

    tests = [
        test_capability_gap_analysis,
        test_subagent_suggestions,
        test_mcp_tool_recommendations,
        test_clone_agent_design,
        test_system_improvement_prioritization,
        test_implementation_plan_generation,
        test_agent_integration,
    ]

    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            logger.error(f"Test {test.__name__} failed with exception: {e}")
            results.append(False)

    # Summary
    passed = sum(results)
    total = len(results)

    print(f"\n📊 EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {passed / total * 100:.1f}%")

    if passed == total:
        print("✅ All meta-cognitive capabilities are working correctly!")
        return 0
    else:
        print("❌ Some meta-cognitive capabilities need attention")
        return 1


async def main():
    """Main evaluation function"""
    try:
        exit_code = await run_all_meta_cognitive_tests()
        return exit_code
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
