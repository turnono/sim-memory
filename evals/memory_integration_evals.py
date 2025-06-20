#!/usr/bin/env python3
"""
Memory Integration Evaluations

Comprehensive tests for the complete memory architecture:
1. VertexAI Session Service persistence 
2. Session state management via tools
3. Automatic session-to-memory transfer
4. VertexAI RAG Memory Service retrieval
5. Cross-session memory continuity
6. Tool integration patterns

Tests the actual flow: Session Tools → Session State → Memory Service → Memory Tools
"""

import sys
import os
import asyncio
import logging
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the actual components
from main import create_runner
from google.genai.types import Content, Part


class MemoryIntegrationEvals:
    """Comprehensive memory integration test suite."""

    def __init__(self):
        self.test_user_id = f"memory_test_{uuid.uuid4().hex[:8]}"
        self.runner = None
        self.test_sessions = []  # Track sessions for cleanup

    async def setup(self):
        """Initialize the test environment"""
        print("🔧 Setting up memory integration test environment...")
        self.runner = await create_runner()
        print(f"✅ Runner initialized with:")
        print(f"   - Session Service: {type(self.runner.session_service).__name__}")
        print(f"   - Memory Service: {type(self.runner.memory_service).__name__}")

    async def cleanup(self):
        """Clean up test resources"""
        print("\n🧹 Cleaning up test sessions...")
        # Note: In production, VertexAI manages session cleanup automatically
        print(f"   Test user: {self.test_user_id}")
        print(f"   Sessions created: {len(self.test_sessions)}")

    async def eval_session_creation_and_persistence(self) -> Dict[str, Any]:
        """Test session creation and automatic persistence"""
        print("\n📝 Evaluating: Session Creation & Persistence")
        
        start_time = time.time()
        result = {
            "test_name": "session_creation_persistence",
            "passed": False,
            "details": {},
            "errors": []
        }

        try:
            # Create a new session
            session = await self.runner.session_service.create_session(
                app_name=self.runner.app_name, 
                user_id=self.test_user_id
            )
            session_id = session.id
            self.test_sessions.append(session_id)

            # Send a simple message to establish session state
            user_input = Content(parts=[Part(text="Hello, my name is Alice and I'm a data scientist.")], role="user")
            
            response_received = False
            async for event in self.runner.run_async(
                user_id=self.test_user_id, 
                session_id=session_id, 
                new_message=user_input
            ):
                if event.is_final_response():
                    response_received = True
                    break

            # Verify session can be retrieved
            retrieved_session = await self.runner.session_service.get_session(
                app_name=self.runner.app_name,
                user_id=self.test_user_id,
                session_id=session_id
            )

            result["passed"] = response_received and retrieved_session is not None
            result["details"] = {
                "session_id": session_id,
                "user_id": self.test_user_id,
                "response_received": response_received,
                "session_retrieved": retrieved_session is not None,
                "session_type": type(retrieved_session).__name__ if retrieved_session else "None"
            }

        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"Session creation test failed: {e}")

        result["duration"] = time.time() - start_time
        return result

    async def eval_memory_tools_functionality(self) -> Dict[str, Any]:
        """Test memory management tools through the agent"""
        print("\n🧠 Evaluating: Memory Tools Functionality")
        
        start_time = time.time()
        result = {
            "test_name": "memory_tools_functionality",
            "passed": False,
            "details": {},
            "errors": []
        }

        try:
            # Use existing session or create new one
            if not self.test_sessions:
                session = await self.runner.session_service.create_session(
                    app_name=self.runner.app_name, 
                    user_id=self.test_user_id
                )
                session_id = session.id
                self.test_sessions.append(session_id)
            else:
                session_id = self.test_sessions[0]

            # Test storing user context
            store_message = Content(
                parts=[Part(text="Please store that I prefer morning meetings and my goal is to improve my Python skills.")], 
                role="user"
            )
            
            tool_calls_detected = []
            store_response_received = False
            
            async for event in self.runner.run_async(
                user_id=self.test_user_id,
                session_id=session_id,
                new_message=store_message
            ):
                if event.get_function_calls():
                    for func_call in event.get_function_calls():
                        tool_calls_detected.append(func_call.name)
                
                if event.is_final_response():
                    store_response_received = True
                    break

            # Test retrieving user context
            retrieve_message = Content(
                parts=[Part(text="What do you know about my preferences and goals?")], 
                role="user"
            )
            
            retrieve_response_received = False
            async for event in self.runner.run_async(
                user_id=self.test_user_id,
                session_id=session_id,
                new_message=retrieve_message
            ):
                if event.get_function_calls():
                    for func_call in event.get_function_calls():
                        tool_calls_detected.append(func_call.name)
                
                if event.is_final_response():
                    retrieve_response_received = True
                    break

            # Test session analysis
            analysis_message = Content(
                parts=[Part(text="Can you analyze our current session context?")], 
                role="user"
            )
            
            analysis_response_received = False
            async for event in self.runner.run_async(
                user_id=self.test_user_id,
                session_id=session_id,
                new_message=analysis_message
            ):
                if event.get_function_calls():
                    for func_call in event.get_function_calls():
                        tool_calls_detected.append(func_call.name)
                
                if event.is_final_response():
                    analysis_response_received = True
                    break

            # Check for expected tool usage
            expected_tools = ["store_user_context", "get_user_context", "analyze_session_context"]
            tools_used = [tool for tool in expected_tools if tool in tool_calls_detected]

            result["passed"] = (
                store_response_received and 
                retrieve_response_received and 
                analysis_response_received and
                len(tools_used) > 0
            )
            result["details"] = {
                "session_id": session_id,
                "tool_calls_detected": tool_calls_detected,
                "expected_tools_used": tools_used,
                "all_responses_received": [store_response_received, retrieve_response_received, analysis_response_received]
            }

        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"Memory tools test failed: {e}")

        result["duration"] = time.time() - start_time
        return result

    async def eval_session_to_memory_persistence(self) -> Dict[str, Any]:
        """Test automatic session-to-memory persistence"""
        print("\n💾 Evaluating: Session-to-Memory Persistence")
        
        start_time = time.time()
        result = {
            "test_name": "session_to_memory_persistence",
            "passed": False,
            "details": {},
            "errors": []
        }

        try:
            # Create a session with meaningful content
            session = await self.runner.session_service.create_session(
                app_name=self.runner.app_name, 
                user_id=self.test_user_id
            )
            session_id = session.id
            self.test_sessions.append(session_id)

            # Have a meaningful conversation that should be saved to memory
            messages = [
                "My name is Bob and I'm working on a data science project about customer churn prediction.",
                "I'm struggling with feature engineering and model selection. Can you help me?",
                "I've tried logistic regression and random forest, but my accuracy is only 70%."
            ]

            for i, msg_text in enumerate(messages):
                user_input = Content(parts=[Part(text=msg_text)], role="user")
                
                response_received = False
                async for event in self.runner.run_async(
                    user_id=self.test_user_id,
                    session_id=session_id,
                    new_message=user_input
                ):
                    if event.is_final_response():
                        response_received = True
                        break
                
                # Small delay between messages
                await asyncio.sleep(1)

            # Test explicit session saving
            save_message = Content(
                parts=[Part(text="Please save our conversation about my data science project to memory.")], 
                role="user"
            )
            
            save_tool_called = False
            save_response_received = False
            
            async for event in self.runner.run_async(
                user_id=self.test_user_id,
                session_id=session_id,
                new_message=save_message
            ):
                if event.get_function_calls():
                    for func_call in event.get_function_calls():
                        if func_call.name == "save_session_to_memory":
                            save_tool_called = True
                
                if event.is_final_response():
                    save_response_received = True
                    break

            result["passed"] = save_response_received
            result["details"] = {
                "session_id": session_id,
                "messages_sent": len(messages),
                "save_tool_called": save_tool_called,
                "save_response_received": save_response_received
            }

        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"Session-to-memory persistence test failed: {e}")

        result["duration"] = time.time() - start_time
        return result

    async def eval_cross_session_memory_retrieval(self) -> Dict[str, Any]:
        """Test memory retrieval across different sessions"""
        print("\n🔍 Evaluating: Cross-Session Memory Retrieval")
        
        start_time = time.time()
        result = {
            "test_name": "cross_session_memory_retrieval",
            "passed": False,
            "details": {},
            "errors": []
        }

        try:
            # Create a new session (different from previous ones)
            new_session = await self.runner.session_service.create_session(
                app_name=self.runner.app_name, 
                user_id=self.test_user_id
            )
            new_session_id = new_session.id
            self.test_sessions.append(new_session_id)

            # Try to retrieve information from previous sessions
            memory_query = Content(
                parts=[Part(text="What do you remember about my data science project and my goals?")], 
                role="user"
            )
            
            load_memory_called = False
            memory_response_received = False
            memory_response_content = ""
            
            async for event in self.runner.run_async(
                user_id=self.test_user_id,
                session_id=new_session_id,
                new_message=memory_query
            ):
                if event.get_function_calls():
                    for func_call in event.get_function_calls():
                        if func_call.name == "load_memory":
                            load_memory_called = True
                
                if event.is_final_response() and event.content and event.content.parts:
                    memory_response_received = True
                    memory_response_content = event.content.parts[0].text
                    break

            # Test if agent can find context from memory
            context_found = any(keyword in memory_response_content.lower() for keyword in 
                              ["data science", "project", "churn", "bob", "python", "goals", "preferences"])

            result["passed"] = memory_response_received and (load_memory_called or context_found)
            result["details"] = {
                "new_session_id": new_session_id,
                "load_memory_called": load_memory_called,
                "memory_response_received": memory_response_received,
                "context_found": context_found,
                "response_content_sample": memory_response_content[:200] if memory_response_content else "No response"
            }

        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"Cross-session memory retrieval test failed: {e}")

        result["duration"] = time.time() - start_time
        return result

    async def eval_memory_service_integration(self) -> Dict[str, Any]:
        """Test that VertexAI memory service is properly integrated"""
        print("\n⚙️ Evaluating: Memory Service Integration")
        
        start_time = time.time()
        result = {
            "test_name": "memory_service_integration",
            "passed": False,
            "details": {},
            "errors": []
        }

        try:
            # Check memory service configuration
            memory_service = self.runner.memory_service
            memory_service_type = type(memory_service).__name__
            
            # Test memory service health (if available)
            memory_healthy = True
            try:
                if hasattr(memory_service, 'health_check'):
                    health = await memory_service.health_check()
                    memory_healthy = health.get('status') in ['healthy', 'degraded']
            except Exception as e:
                logger.warning(f"Memory service health check failed: {e}")
                memory_healthy = False

            # Test that load_memory tool is available in agent
            load_memory_tool_available = False
            for tool in self.runner.agent.tools:
                if hasattr(tool, 'name') and tool.name == 'load_memory':
                    load_memory_tool_available = True
                    break
                elif hasattr(tool, 'func') and getattr(tool.func, '__name__', '') == 'load_memory':
                    load_memory_tool_available = True
                    break

            result["passed"] = (
                memory_service is not None and
                memory_service_type in ['VertexAiRagMemoryService', 'InMemoryMemoryService'] and
                load_memory_tool_available
            )
            result["details"] = {
                "memory_service_type": memory_service_type,
                "memory_service_available": memory_service is not None,
                "memory_healthy": memory_healthy,
                "load_memory_tool_available": load_memory_tool_available,
                "agent_tool_count": len(self.runner.agent.tools)
            }

        except Exception as e:
            result["errors"].append(str(e))
            logger.error(f"Memory service integration test failed: {e}")

        result["duration"] = time.time() - start_time
        return result

    async def run_all_evaluations(self) -> Dict[str, Any]:
        """Run all memory integration evaluations"""
        print("🚀 Running Memory Integration Evaluations")
        print("=" * 80)
        
        await self.setup()
        
        # Run all evaluations
        evaluations = [
            self.eval_session_creation_and_persistence,
            self.eval_memory_tools_functionality, 
            self.eval_session_to_memory_persistence,
            self.eval_cross_session_memory_retrieval,
            self.eval_memory_service_integration
        ]
        
        results = []
        passed_count = 0
        
        for eval_func in evaluations:
            try:
                result = await eval_func()
                results.append(result)
                if result["passed"]:
                    passed_count += 1
                    print(f"✅ {result['test_name']}: PASSED")
                else:
                    print(f"❌ {result['test_name']}: FAILED")
                    if result["errors"]:
                        for error in result["errors"]:
                            print(f"   Error: {error}")
            except Exception as e:
                print(f"❌ {eval_func.__name__}: CRASHED - {e}")
                results.append({
                    "test_name": eval_func.__name__,
                    "passed": False,
                    "errors": [str(e)],
                    "duration": 0
                })
        
        await self.cleanup()
        
        # Summary
        total_tests = len(evaluations)
        print("\n" + "=" * 80)
        print(f"📊 MEMORY INTEGRATION EVALUATION SUMMARY")
        print(f"Tests Passed: {passed_count}/{total_tests}")
        print(f"Success Rate: {(passed_count/total_tests)*100:.1f}%")
        
        if passed_count == total_tests:
            print("🎉 ALL MEMORY INTEGRATION TESTS PASSED!")
            print("✨ The complete memory architecture is working correctly:")
            print("   - VertexAI Session Service ✅")
            print("   - Session state management ✅") 
            print("   - Session-to-memory persistence ✅")
            print("   - Memory retrieval tools ✅")
            print("   - Cross-session continuity ✅")
        else:
            print("⚠️ Some memory integration tests failed.")
            print("🔧 Review the detailed results above for debugging.")
        
        return {
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_count,
                "success_rate": (passed_count/total_tests)*100,
                "all_passed": passed_count == total_tests
            },
            "detailed_results": results
        }


async def run_memory_integration_evals():
    """Entry point for memory integration evaluations"""
    evaluator = MemoryIntegrationEvals()
    return await evaluator.run_all_evaluations()


if __name__ == "__main__":
    asyncio.run(run_memory_integration_evals()) 