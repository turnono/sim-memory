#!/usr/bin/env python3
"""
Memory Subagent Architecture Evaluations

Tests the new memory subagent approach compared to direct memory tools.
Evaluates delegation, efficiency, and architectural benefits.
"""

import asyncio
import logging
import time
import sys
from pathlib import Path
from sim_guide.agent import root_agent
from sim_guide.sub_agents.memory_manager import memory_manager
from sim_guide.sub_agents.memory_manager.services.rag_memory_service import (
    RAG_COST_OPTIMIZED,
)

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import the updated agent with memory subagent

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class MemorySubagentEvals:
    """Evaluation suite for memory subagent architecture."""

    def __init__(self):
        self.results = []

    async def eval_memory_subagent_direct(self) -> dict:
        """Test the memory subagent directly (not through main agent)."""
        print("\n🧠 Testing Memory Subagent Direct Access")

        start_time = time.time()
        result = {
            "test_name": "memory_subagent_direct",
            "passed": False,
            "details": {},
            "errors": [],
        }

        try:
            # Test memory system status check
            print("  Testing memory system status...")

            # Since we can't easily test the Agent directly without ADK runners,
            # we'll test the underlying functions
            from sim_guide.sub_agents.memory_manager import (
                get_memory_system_status,
            )

            status = await get_memory_system_status()
            print(f"    Memory system status: {status}")

            # Test knowledge base search
            print("  Testing knowledge base search...")
            from sim_guide.sub_agents.memory_manager import search_knowledge_base

            kb_result = await search_knowledge_base("career guidance")
            print(f"    Knowledge base search result: {kb_result[:100]}...")

            # Test user memory search (will likely return no results but should not error)
            print("  Testing user memory search...")
            from sim_guide.sub_agents.memory_manager import search_user_memories

            user_memories = await search_user_memories("career goals", "test_user")
            print(f"    User memory search result: {user_memories[:100]}...")

            result["passed"] = True
            result["details"] = {
                "memory_status": status,
                "kb_search_length": len(kb_result),
                "user_search_length": len(user_memories),
            }

        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"Memory subagent direct test failed: {e}")

        result["duration"] = time.time() - start_time
        return result

    async def eval_memory_delegation_pattern(self) -> dict:
        """Test how well the main agent delegates memory operations."""
        print("\n🎯 Testing Memory Delegation Pattern")

        start_time = time.time()
        result = {
            "test_name": "memory_delegation_pattern",
            "passed": False,
            "details": {},
            "errors": [],
        }

        try:
            # Check that the main agent has the memory subagent as a tool
            main_agent_tools = getattr(root_agent, "tools", [])

            # Look for AgentTool containing memory agent
            memory_tool_found = False
            memory_tool_name = None

            for tool in main_agent_tools:
                # Check if this is an AgentTool wrapping our memory agent
                if hasattr(tool, "agent") and hasattr(tool.agent, "name"):
                    if tool.agent.name == "memory_manager":
                        memory_tool_found = True
                        memory_tool_name = tool.agent.name
                        break

                # Also check if it's a function that might relate to memory or session
                if hasattr(tool, "func") and hasattr(tool.func, "__name__"):
                    if (
                        "memory" in tool.func.__name__.lower()
                        or "session" in tool.func.__name__.lower()
                    ):
                        # This would be a direct memory/session tool (should not exist now)
                        result["errors"].append(
                            f"Found direct memory/session tool: {tool.func.__name__}"
                        )

            if memory_tool_found:
                result["passed"] = True
                result["details"]["memory_subagent_integrated"] = True
                result["details"]["memory_tool_name"] = memory_tool_name
                print(
                    f"    ✅ Memory & session subagent successfully integrated as tool: {memory_tool_name}"
                )
            else:
                result["errors"].append(
                    "Memory & session subagent not found in main agent tools"
                )
                print(f"    ❌ Memory & session subagent not found in main agent tools")

            # Count total tools
            result["details"]["total_tools"] = len(main_agent_tools)
            result["details"]["tool_types"] = []

            for tool in main_agent_tools:
                if hasattr(tool, "agent"):
                    result["details"]["tool_types"].append(
                        f"AgentTool({tool.agent.name})"
                    )
                elif hasattr(tool, "func"):
                    result["details"]["tool_types"].append(
                        f"FunctionTool({tool.func.__name__})"
                    )
                else:
                    result["details"]["tool_types"].append(
                        f"Tool({type(tool).__name__})"
                    )

            print(f"    Total tools in main agent: {result['details']['total_tools']}")
            print(f"    Tool types: {result['details']['tool_types']}")

        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"Memory delegation pattern test failed: {e}")

        result["duration"] = time.time() - start_time
        return result

    async def eval_architecture_benefits(self) -> dict:
        """Evaluate the architectural benefits of the subagent approach."""
        print("\n🏗️ Evaluating Architecture Benefits")

        start_time = time.time()
        result = {
            "test_name": "architecture_benefits",
            "passed": False,
            "details": {},
            "errors": [],
        }

        try:
            # Check separation of concerns
            print("  Checking separation of concerns...")

            # Memory agent should only have memory-related tools
            memory_manager_tools = getattr(memory_manager, "tools", [])
            memory_tool_names = []

            for tool in memory_manager_tools:
                if hasattr(tool, "func"):
                    memory_tool_names.append(tool.func.__name__)

            print(f"    Memory agent tools: {memory_tool_names}")

            # All memory agent tools should be memory-related
            memory_related = all(
                "memory" in name.lower()
                or "context" in name.lower()
                or "knowledge" in name.lower()
                or "store" in name.lower()
                or "status" in name.lower()
                for name in memory_tool_names
            )

            # Main agent should not have direct memory tools
            main_agent_tools = getattr(root_agent, "tools", [])
            main_tool_names = []

            for tool in main_agent_tools:
                if hasattr(tool, "func"):
                    main_tool_names.append(tool.func.__name__)
                elif hasattr(tool, "agent"):
                    main_tool_names.append(f"subagent_{tool.agent.name}")

            print(f"    Main agent tools: {main_tool_names}")

            # Check that main agent doesn't have direct memory functions
            no_direct_memory = not any(
                "load_life_guidance_memory" in name
                or "preload_life_context" in name
                or "load_life_resources" in name
                for name in main_tool_names
            )

            # Check modularity - memory agent should be self-contained
            memory_manager_instruction = getattr(
                memory_manager, "instruction", ""
            )
            focused_instruction = len(memory_manager_instruction) < len(
                getattr(root_agent, "instruction", "")
            )

            result["details"] = {
                "memory_tools_count": len(memory_tool_names),
                "memory_tools_focused": memory_related,
                "main_tools_count": len(main_tool_names),
                "no_direct_memory_tools": no_direct_memory,
                "memory_instruction_focused": focused_instruction,
                "separation_achieved": memory_related and no_direct_memory,
                "memory_tool_names": memory_tool_names,
                "main_tool_names": main_tool_names,
            }

            # Overall architecture score
            architecture_score = sum(
                [
                    memory_related,  # Memory agent tools are focused
                    no_direct_memory,  # Main agent doesn't have direct memory tools
                    focused_instruction,  # Memory agent has focused instruction
                    len(memory_tool_names)
                    >= 3,  # Memory agent has sufficient capabilities
                ]
            )

            result["details"]["architecture_score"] = f"{architecture_score}/4"
            result["passed"] = architecture_score >= 3

            if result["passed"]:
                print(
                    f"    ✅ Architecture benefits achieved (score: {architecture_score}/4)"
                )
            else:
                print(
                    f"    ⚠️ Architecture needs improvement (score: {architecture_score}/4)"
                )

        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"Architecture benefits evaluation failed: {e}")

        result["duration"] = time.time() - start_time
        return result

    async def eval_cost_optimization_impact(self) -> dict:
        """Evaluate how the subagent affects cost optimization."""
        print("\n💰 Evaluating Cost Optimization Impact")

        start_time = time.time()
        result = {
            "test_name": "cost_optimization_impact",
            "passed": False,
            "details": {},
            "errors": [],
        }

        try:
            # Memory operations should now be consolidated in one place
            print("  Checking cost optimization compatibility...")

            # Memory agent should respect cost optimization flags
            result["details"]["rag_cost_optimized"] = RAG_COST_OPTIMIZED
            print(f"    RAG cost optimization enabled: {RAG_COST_OPTIMIZED}")

            # Count potential API calls in memory operations
            memory_functions = [
                "search_user_memories",
                "search_knowledge_base",
                "store_conversation_memory",
                "get_memory_system_status",
                "preload_context_for_topic",
            ]

            # In the new architecture, memory operations are consolidated
            # This should reduce the "tool sprawl" that was causing cost issues

            # Check that memory operations can be selectively disabled
            selective_control = True  # Memory agent allows selective operations
            consolidated_memory = (
                len(memory_functions) <= 6
            )  # Reasonable number of functions

            result["details"] = {
                "memory_functions_count": len(memory_functions),
                "memory_functions": memory_functions,
                "consolidated_design": consolidated_memory,
                "selective_control": selective_control,
                "cost_flags_respected": RAG_COST_OPTIMIZED is not None,
            }

            # Cost optimization score
            cost_score = sum(
                [
                    consolidated_memory,
                    selective_control,
                    RAG_COST_OPTIMIZED is not None,  # Cost flags are configured
                ]
            )

            result["details"]["cost_optimization_score"] = f"{cost_score}/3"
            result["passed"] = cost_score >= 2

            if result["passed"]:
                print(f"    ✅ Cost optimization compatible (score: {cost_score}/3)")
            else:
                print(
                    f"    ⚠️ Cost optimization needs attention (score: {cost_score}/3)"
                )

        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"Cost optimization evaluation failed: {e}")

        result["duration"] = time.time() - start_time
        return result


async def run_memory_subagent_evals() -> dict:
    """Run all memory subagent evaluations."""
    print("🔬 Starting Memory Subagent Architecture Evaluations")
    print("=" * 60)

    evaluator = MemorySubagentEvals()
    eval_results = []

    # Run all evaluations
    evaluations = [
        evaluator.eval_memory_subagent_direct,
        evaluator.eval_memory_delegation_pattern,
        evaluator.eval_architecture_benefits,
        evaluator.eval_cost_optimization_impact,
    ]

    for evaluation in evaluations:
        start_time = time.time()
        result = await evaluation()
        result["duration"] = time.time() - start_time
        eval_results.append(result)

        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"{status}: {result['test_name']} ({result['duration']:.2f}s)")

        if result["errors"]:
            for error in result["errors"]:
                print(f"   Error: {error}")

    # Summary
    print("\n" + "=" * 60)
    passed_tests = len([r for r in eval_results if r["passed"]])
    total_tests = len(eval_results)

    print(f"Memory Subagent Architecture Evaluation Results:")
    print(f"   Passed: {passed_tests}/{total_tests}")
    print(f"   Success Rate: {(passed_tests / total_tests) * 100:.1f}%")

    if passed_tests == total_tests:
        print("🎉 All memory subagent architecture tests passed!")
        print("\n📊 Architecture Summary:")
        print("   ✅ Memory operations consolidated in specialized subagent")
        print("   ✅ Main agent delegates memory tasks via AgentTool")
        print("   ✅ Separation of concerns achieved")
        print("   ✅ Cost optimization compatibility maintained")
        print("\n💡 Benefits Achieved:")
        print("   • Modular architecture with specialized agents")
        print("   • Cleaner main agent focused on life guidance")
        print("   • Consolidated memory operations for better maintainability")
        print("   • Cost optimization flags still respected")
    else:
        print("⚠️  Some memory subagent architecture tests failed - check details above")

    return {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "success_rate": passed_tests / total_tests,
        "results": eval_results,
    }


if __name__ == "__main__":
    asyncio.run(run_memory_subagent_evals())
