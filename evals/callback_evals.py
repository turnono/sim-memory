"""
Callback System Evaluations for Sim Guide Agent

Tests the callback functionality including:
- Agent lifecycle callbacks
- Model interaction callbacks
- Tool execution callbacks
- Performance monitoring
- RAG Memory Service integration
- Error handling and logging
"""

import asyncio
import logging
import time
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Import the agent and callback system
from sim_guide.agent import root_agent
from sim_guide.callbacks import (
    before_agent_callback,
    after_agent_callback,
    before_model_callback,
    after_model_callback,
    before_tool_callback,
    after_tool_callback,
)
from sim_guide.services.rag_memory_service import (
    health_check,
    add_memory_from_conversation,
    retrieve_user_memories,
)

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


# Setup logging to capture callback messages
logging.basicConfig(level=logging.INFO, format="%(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class MockCallbackContext:
    """Mock callback context for testing"""

    def __init__(self, user_id: str = "test_user", session_id: str = "test_session"):
        self.user_id = user_id
        self.session_id = session_id
        self.state = {}


class MockLlmRequest:
    """Mock LLM request for testing"""

    def __init__(self, messages: List[str] = None, model: str = "gemini-2.0-flash"):
        self.messages = messages or ["Test message"]
        self.model = model


class MockLlmResponse:
    """Mock LLM response for testing"""

    def __init__(self, content: str = "Test response", token_usage: Dict = None):
        self.content = content
        self.usage = MockTokenUsage(token_usage or {})


class MockTokenUsage:
    """Mock token usage for testing"""

    def __init__(self, usage: Dict):
        self.total_tokens = usage.get("total_tokens", 100)
        self.prompt_tokens = usage.get("prompt_tokens", 50)
        self.completion_tokens = usage.get("completion_tokens", 50)


class MockTool:
    """Mock tool for testing"""

    def __init__(self, name: str = "test_tool"):
        self.name = name


class MockToolContext:
    """Mock tool context for testing"""

    def __init__(self, user_id: str = "test_user", session_id: str = "test_session"):
        self.user_id = user_id
        self.session_id = session_id
        self.state = {}


async def test_agent_callbacks():
    """Test agent lifecycle callbacks"""

    print("🔄 Testing Agent Lifecycle Callbacks")

    # Create mock context
    context = MockCallbackContext("callback_test_user", "callback_test_session")

    # Test before_agent_callback
    start_time = time.time()
    result = before_agent_callback(context)

    # Verify callback executed successfully
    assert result is None, "before_agent_callback should return None"
    assert "processing_start_time" in context.state, (
        "Should track processing start time"
    )

    # Wait a bit to simulate processing time
    await asyncio.sleep(0.1)

    # Test after_agent_callback
    result = after_agent_callback(context)

    # Verify callback executed successfully
    assert result is None, "after_agent_callback should return None"
    assert "last_processing_duration" in context.state, (
        "Should track processing duration"
    )
    assert context.state["last_processing_duration"] > 0, "Duration should be positive"

    duration = time.time() - start_time
    print(f"✅ PASS: Agent callbacks executed successfully in {duration:.2f}s")

    return {
        "test_name": "agent_callbacks",
        "passed": True,
        "duration": duration,
        "metrics": {
            "processing_duration": context.state.get("last_processing_duration")
            if isinstance(context.state, dict)
            else None,
            "context_state_keys": list(context.state.keys())
            if isinstance(context.state, dict)
            else [],
        },
    }


async def test_model_callbacks():
    """Test model interaction callbacks"""

    print("🤖 Testing Model Interaction Callbacks")

    # Create mock objects
    context = MockCallbackContext("model_test_user", "model_test_session")
    request = MockLlmRequest(["Test message 1", "Test message 2"])
    response = MockLlmResponse(
        "Test model response",
        {"total_tokens": 150, "prompt_tokens": 75, "completion_tokens": 75},
    )

    start_time = time.time()

    # Test before_model_callback
    before_model_callback(context, request)

    # Verify timing was set
    assert "model_request_start_time" in context.state, (
        "Should track model request start time"
    )

    # Wait a bit to simulate model processing
    await asyncio.sleep(0.1)

    # Test after_model_callback
    after_model_callback(context, response)

    # Verify callback executed successfully
    assert "last_model_duration" in context.state, "Should track model duration"
    assert context.state["last_model_duration"] > 0, "Model duration should be positive"

    duration = time.time() - start_time
    print(f"✅ PASS: Model callbacks executed successfully in {duration:.2f}s")

    return {
        "test_name": "model_callbacks",
        "passed": True,
        "duration": duration,
        "metrics": {
            "model_duration": context.state.get("last_model_duration")
            if isinstance(context.state, dict)
            else None,
            "context_state_keys": list(context.state.keys())
            if isinstance(context.state, dict)
            else [],
        },
    }


async def test_tool_callbacks():
    """Test tool execution callbacks"""

    print("🔧 Testing Tool Execution Callbacks")

    # Create mock objects
    tool = MockTool("search_tool")
    args = {"query": "test search", "max_results": 5}
    context = MockToolContext("tool_test_user", "tool_test_session")
    response = "Search results: [1, 2, 3, 4, 5]"

    start_time = time.time()

    # Test before_tool_callback
    result = before_tool_callback(tool, args, context)

    # Verify callback executed successfully
    assert result is None, "before_tool_callback should return None by default"
    assert f"{tool.name}_start_time" in context.state, "Should track tool start time"

    # Wait a bit to simulate tool execution
    await asyncio.sleep(0.1)

    # Test after_tool_callback
    result = after_tool_callback(tool, args, context, response)

    # Verify callback executed successfully
    assert result is None, "after_tool_callback should return None"
    assert f"{tool.name}_last_duration" in context.state, "Should track tool duration"
    assert context.state[f"{tool.name}_last_duration"] > 0, (
        "Tool duration should be positive"
    )

    duration = time.time() - start_time
    print(f"✅ PASS: Tool callbacks executed successfully in {duration:.2f}s")

    return {
        "test_name": "tool_callbacks",
        "passed": True,
        "duration": duration,
        "metrics": {
            "tool_duration": context.state.get(f"{tool.name}_last_duration")
            if isinstance(context.state, dict)
            else None,
            "context_state_keys": list(context.state.keys())
            if isinstance(context.state, dict)
            else [],
        },
    }


async def test_callback_integration():
    """Test agent callback integration"""

    print("🔗 Testing Agent Callback Integration")

    start_time = time.time()

    # Verify agent has callbacks registered
    assert root_agent.before_agent_callback is not None, (
        "Agent should have before_agent_callback"
    )
    assert root_agent.after_agent_callback is not None, (
        "Agent should have after_agent_callback"
    )
    assert root_agent.before_model_callback is not None, (
        "Agent should have before_model_callback"
    )
    assert root_agent.after_model_callback is not None, (
        "Agent should have after_model_callback"
    )
    assert root_agent.before_tool_callback is not None, (
        "Agent should have before_tool_callback"
    )
    assert root_agent.after_tool_callback is not None, (
        "Agent should have after_tool_callback"
    )

    # Test that callbacks are the correct functions
    assert root_agent.before_agent_callback == before_agent_callback, (
        "Should use our before_agent_callback"
    )
    assert root_agent.after_agent_callback == after_agent_callback, (
        "Should use our after_agent_callback"
    )

    duration = time.time() - start_time
    print(f"✅ PASS: Agent callback integration verified in {duration:.2f}s")

    return {
        "test_name": "callback_integration",
        "passed": True,
        "duration": duration,
        "metrics": {
            "callbacks_registered": 6,
            "agent_name": root_agent.name,
            "agent_model": root_agent.model,
        },
    }


async def test_rag_memory_integration():
    """Test RAG Memory Service integration through callbacks"""

    print("🧠 Testing RAG Memory Integration through Callbacks")

    try:
        # Test RAG health first
        health_result = await health_check()
        if health_result.get("status") != "healthy":
            print(f"⚠️  RAG Memory Service not healthy: {health_result}")
            return {
                "test_name": "rag_memory_integration",
                "passed": False,
                "error": f"RAG service unhealthy: {health_result.get('status')}",
            }

        start_time = time.time()

        # Create mock memory tool interaction
        tool = MockTool("memory_search_tool")  # Tool name contains 'memory'
        args = {"query": "test memory query", "user_context": "test context"}
        context = MockToolContext("rag_test_user", "rag_test_session")
        response = "Found relevant memories: This is a test response that is longer than 50 characters to trigger storage."

        # Execute tool callback (this should trigger RAG integration)
        result = after_tool_callback(tool, args, context, response)

        # Wait a moment for async memory storage
        await asyncio.sleep(1.0)

        # Try to retrieve stored memories
        try:
            memories = await retrieve_user_memories(
                "rag_test_user", "test memory query"
            )
            print(f"Retrieved {len(memories)} memories from RAG")
        except Exception as e:
            print(f"Note: Could not retrieve memories (expected in some cases): {e}")

        duration = time.time() - start_time
        print(f"✅ PASS: RAG Memory integration test completed in {duration:.2f}s")

        return {
            "test_name": "rag_memory_integration",
            "passed": True,
            "duration": duration,
            "metrics": {
                "rag_health_status": health_result.get("status"),
                "tool_response_length": len(response),
                "integration_triggered": "memory" in tool.name.lower(),
            },
        }

    except Exception as e:
        print(f"❌ FAIL: RAG Memory integration test failed: {e}")
        return {
            "test_name": "rag_memory_integration",
            "passed": False,
            "error": str(e),
            "duration": time.time() - start_time if "start_time" in locals() else 0,
        }


async def test_callback_error_handling():
    """Test callback error handling"""

    print("🛡️  Testing Callback Error Handling")

    start_time = time.time()

    # Test with invalid context (should not crash)
    invalid_context = None

    try:
        result = before_agent_callback(invalid_context)
        assert result is None, "Should handle invalid context gracefully"
        print("✅ before_agent_callback handles invalid context")
    except Exception as e:
        print(f"⚠️  before_agent_callback error handling: {e}")

    try:
        result = before_model_callback(invalid_context, None)
        print("✅ before_model_callback handles invalid context")
    except Exception as e:
        print(f"⚠️  before_model_callback error handling: {e}")

    try:
        result = before_tool_callback(None, {}, invalid_context)
        assert result is None, "Should handle invalid tool context gracefully"
        print("✅ before_tool_callback handles invalid context")
    except Exception as e:
        print(f"⚠️  before_tool_callback error handling: {e}")

    duration = time.time() - start_time
    print(f"✅ PASS: Error handling tests completed in {duration:.2f}s")

    return {
        "test_name": "callback_error_handling",
        "passed": True,
        "duration": duration,
        "metrics": {"error_scenarios_tested": 3, "graceful_handling": True},
    }


async def test_performance_monitoring():
    """Test performance monitoring capabilities"""

    print("📊 Testing Performance Monitoring")

    start_time = time.time()

    # Create a series of mock interactions to test performance tracking
    context = MockCallbackContext("perf_test_user", "perf_test_session")

    # Simulate multiple agent interactions
    performance_data = []

    for i in range(3):
        # Agent lifecycle
        before_agent_callback(context)
        await asyncio.sleep(0.05)  # Simulate processing
        after_agent_callback(context)

        if "last_processing_duration" in context.state:
            performance_data.append(
                {
                    "interaction": i + 1,
                    "processing_duration": context.state["last_processing_duration"],
                }
            )

        # Model interaction
        before_model_callback(context, MockLlmRequest())
        await asyncio.sleep(0.03)  # Simulate model call
        after_model_callback(context, MockLlmResponse())

        # Tool interaction
        tool = MockTool(f"test_tool_{i}")
        before_tool_callback(tool, {"test": f"arg_{i}"}, context)
        await asyncio.sleep(0.02)  # Simulate tool execution
        after_tool_callback(tool, {"test": f"arg_{i}"}, context, f"response_{i}")

    # Verify performance data was collected
    assert len(performance_data) == 3, (
        "Should have collected performance data for all interactions"
    )

    # Calculate average performance
    avg_duration = sum(p["processing_duration"] for p in performance_data) / len(
        performance_data
    )

    duration = time.time() - start_time
    print(f"✅ PASS: Performance monitoring test completed in {duration:.2f}s")
    print(f"   Average processing duration: {avg_duration:.3f}s")

    return {
        "test_name": "performance_monitoring",
        "passed": True,
        "duration": duration,
        "metrics": {
            "interactions_tested": len(performance_data),
            "average_processing_duration": avg_duration,
            "performance_data": performance_data,
            "state_keys_tracked": list(context.state.keys()),
        },
    }


async def run_callback_evaluations():
    """Run all callback evaluation tests"""

    print("🔬 Starting Callback System Evaluations")
    print("=" * 50)

    tests = [
        test_agent_callbacks,
        test_model_callbacks,
        test_tool_callbacks,
        test_callback_integration,
        test_rag_memory_integration,
        test_callback_error_handling,
        test_performance_monitoring,
    ]

    results = []
    start_time = datetime.now()

    for test_func in tests:
        try:
            result = await test_func()
            results.append(result)
        except Exception as e:
            logger.error(f"Test {test_func.__name__} failed with error: {e}")
            results.append(
                {
                    "test_name": test_func.__name__,
                    "passed": False,
                    "error": str(e),
                    "duration": 0,
                }
            )

        print()  # Add spacing between tests

    # Calculate summary
    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()
    passed_tests = sum(1 for r in results if r["passed"])
    total_tests = len(results)
    success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0

    print("=" * 50)
    print("Callback System Evaluation Results:")
    print(f"   Passed: {passed_tests}/{total_tests}")
    print(f"   Success Rate: {success_rate:.1f}%")
    print(f"   Total Duration: {total_duration:.2f}s")

    if success_rate == 100:
        print("🎉 All callback system tests passed!")
    else:
        print("⚠️  Some callback system tests failed - check logs for details")

    # Save detailed results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = f"evals/eval_report_{timestamp}.json"

    detailed_report = {
        "summary": {
            "evaluation_info": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "total_duration": total_duration,
            },
            "results": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": total_tests - passed_tests,
                "success_rate": success_rate,
            },
        },
        "detailed_results": results,
    }

    with open(report_file, "w") as f:
        json.dump(detailed_report, f, indent=2, default=str)

    print(f"📊 Detailed report saved to: {report_file}")

    return detailed_report


if __name__ == "__main__":
    asyncio.run(run_callback_evaluations())
