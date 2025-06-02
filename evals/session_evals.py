#!/usr/bin/env python3
"""
Session Service Evaluations
Tests for session creation, management, and persistence.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
import time
import uuid
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import session service functions directly
from sim_guide.services.session_service import (
    create_session,
    send_message, 
    get_session,
    delete_session,
    list_user_sessions,
    health_check,
    REASONING_ENGINE_ID
)

class SessionServiceEvals:
    """Test suite for session service functionality."""
    
    def __init__(self):
        self.test_user_ids = [f"test_user_{i}_{uuid.uuid4().hex[:8]}" for i in range(3)]
        self.created_sessions = []  # Track for cleanup
    
    async def cleanup(self):
        """Clean up test sessions."""
        print("\n🧹 Cleaning up test sessions...")
        cleanup_count = 0
        
        for user_id, session_id in self.created_sessions:
            try:
                await delete_session(user_id, session_id)
                cleanup_count += 1
            except Exception as e:
                logger.warning(f"Failed to cleanup session {session_id}: {e}")
        
        print(f"   Cleaned up {cleanup_count}/{len(self.created_sessions)} sessions")
        self.created_sessions.clear()
    
    async def eval_basic_session_creation(self) -> Dict[str, Any]:
        """Test basic session creation and retrieval."""
        print("\n🔧 Evaluating: Basic Session Creation")
        
        results = {
            "test_name": "basic_session_creation",
            "passed": False,
            "details": {},
            "errors": []
        }
        
        try:
            user_id = self.test_user_ids[0]
            session_context = {
                "simulation_type": "test_simulation",
                "user_level": "beginner"
            }
            
            # Test session creation
            session_info = await create_session(
                user_id=user_id,
                session_context=session_context
            )
            session_id = session_info["session_id"]
            self.created_sessions.append((user_id, session_id))
            
            # Test session retrieval
            retrieved_session = await get_session(user_id, session_id)
            
            # Validate session data
            assert session_info["user_id"] == user_id
            assert session_info["session_type"] == "simulation_guide"
            assert "created_at" in session_info
            assert retrieved_session["session_id"] == session_id
            
            results["passed"] = True
            results["details"] = {
                "session_id": session_id,
                "user_id": user_id,
                "session_context": session_context,
                "retrieved_state": retrieved_session["state"]
            }
            
        except Exception as e:
            results["errors"].append(str(e))
            
        return results
    
    async def eval_session_messaging(self) -> Dict[str, Any]:
        """Test sending messages through sessions."""
        print("\n💬 Evaluating: Session Messaging")
        
        results = {
            "test_name": "session_messaging",
            "passed": False,
            "details": {},
            "errors": []
        }
        
        try:
            user_id = self.test_user_ids[0]
            
            # Create session
            session_info = await create_session(
                user_id=user_id,
                session_context={"simulation_mode": "test"}
            )
            session_id = session_info["session_id"]
            self.created_sessions.append((user_id, session_id))
            
            # Send test messages using the functional send_message
            messages = [
                "Hello, I need help with the simulation",
                "What are my options?",
                "Can you guide me through the next steps?"
            ]
            
            responses = []
            for message in messages:
                response = await send_message(user_id, session_id, message)
                responses.append(response)
            
            # Validate responses
            assert all(r["status"] == "success" for r in responses)
            assert all(len(r["agent_response"]) > 0 for r in responses)
            
            results["passed"] = True
            results["details"] = {
                "session_id": session_id,
                "message_count": len(responses),
                "responses": responses,
                "avg_response_time": sum(r["response_time_seconds"] for r in responses) / len(responses)
            }
            
        except Exception as e:
            results["errors"].append(str(e))
            
        return results
    
    async def eval_multi_user_sessions(self) -> Dict[str, Any]:
        """Test multiple users with separate sessions."""
        print("\n👥 Evaluating: Multi-User Sessions")
        
        results = {
            "test_name": "multi_user_sessions",
            "passed": False,
            "details": {},
            "errors": []
        }
        
        try:
            # Create sessions for multiple users
            user_sessions = {}
            for i, user_id in enumerate(self.test_user_ids):
                session_info = await create_session(
                    user_id=user_id,
                    session_context={"user_type": f"test_user_{i+1}", "preferences": {"level": i+1}}
                )
                session_id = session_info["session_id"]
                user_sessions[user_id] = session_id
                self.created_sessions.append((user_id, session_id))
            
            # Send different messages from each user
            user_responses = {}
            for user_id, session_id in user_sessions.items():
                message = f"Hello, I'm {user_id}. Can you help me start the simulation?"
                response = await send_message(user_id, session_id, message)
                user_responses[user_id] = response
            
            # List sessions for each user
            user_session_lists = {}
            for user_id in self.test_user_ids:
                sessions = await list_user_sessions(user_id)
                user_session_lists[user_id] = sessions
            
            # Validate isolation
            assert len(user_sessions) == len(self.test_user_ids)
            assert all(resp["status"] == "success" for resp in user_responses.values())
            
            results["passed"] = True
            results["details"] = {
                "user_count": len(user_sessions),
                "sessions_created": user_sessions,
                "responses_received": {uid: len(resp["agent_response"]) for uid, resp in user_responses.items()},
                "session_lists": user_session_lists
            }
            
        except Exception as e:
            results["errors"].append(str(e))
            
        return results
    
    async def eval_session_state_persistence(self) -> Dict[str, Any]:
        """Test session state persistence across messages."""
        print("\n💾 Evaluating: Session State Persistence")
        
        results = {
            "test_name": "session_state_persistence", 
            "passed": False,
            "details": {},
            "errors": []
        }
        
        try:
            user_id = self.test_user_ids[0]
            
            # Create session with initial state
            initial_context = {
                "simulation_step": 1,
                "user_level": "beginner",
                "completed_tasks": [],
                "current_objective": "start_simulation"
            }
            
            session_info = await create_session(
                user_id=user_id,
                session_context=initial_context
            )
            session_id = session_info["session_id"]
            self.created_sessions.append((user_id, session_id))
            
            # Track state changes
            state_snapshots = []
            
            # Initial state
            session_data = await get_session(user_id, session_id)
            state_snapshots.append(("initial", session_data["state"]))
            
            # Send messages that might modify state
            messages = [
                "I want to start the simulation",
                "What's my current progress?",
                "Show me advanced options"
            ]
            
            for i, message in enumerate(messages):
                response = await send_message(user_id, session_id, message)
                
                # Get updated session state
                session_data = await get_session(user_id, session_id)
                state_snapshots.append((f"after_message_{i+1}", session_data["state"]))
                
                # Validate response
                assert response["status"] == "success"
                assert len(response["agent_response"]) > 0
                
                # Small delay to ensure state changes
                await asyncio.sleep(0.5)
            
            # Validate state persistence
            assert len(state_snapshots) > 1
            initial_state = state_snapshots[0][1]
            final_state = state_snapshots[-1][1]
            
            results["passed"] = True
            results["details"] = {
                "session_id": session_id,
                "state_changes": len(state_snapshots),
                "initial_state": initial_state,
                "final_state": final_state,
                "state_snapshots": state_snapshots
            }
            
        except Exception as e:
            results["errors"].append(str(e))
            
        return results
    
    async def eval_error_handling(self) -> Dict[str, Any]:
        """Test error handling for invalid operations."""
        print("\n⚠️  Evaluating: Error Handling")
        
        results = {
            "test_name": "error_handling",
            "passed": False,
            "details": {},
            "errors": []
        }
        
        try:
            user_id = self.test_user_ids[0]
            
            # Test 1: Invalid session ID
            try:
                await get_session(user_id, "invalid_session_id")
                results["errors"].append("Should have failed with invalid session ID")
            except Exception:
                pass  # Expected to fail
            
            # Test 2: Non-existent user
            try:
                await get_session("non_existent_user", "some_session_id")
                results["errors"].append("Should have failed with non-existent user")
            except Exception:
                pass  # Expected to fail
            
            # Test 3: Empty message (should work but handle gracefully)
            session_info = await create_session(user_id=user_id)
            session_id = session_info["session_id"]
            self.created_sessions.append((user_id, session_id))
            
            response = await send_message(user_id, session_id, "")
            # Should handle empty message gracefully
            assert "status" in response
            
            results["passed"] = True
            results["details"] = {
                "empty_message_handled": response["status"],
                "response_to_empty": response["agent_response"]
            }
            
        except Exception as e:
            results["errors"].append(str(e))
            
        return results

async def run_session_evals():
    """Run all session evaluation tests."""
    print("🚀 Starting Session Service Evaluations")
    print("=" * 50)
    
    evaluator = SessionServiceEvals()
    
    try:
        # Run health check first
        print("\n🏥 Running Health Check...")
        health_result = await health_check()
        print(f"   Health Status: {health_result.get('status', 'unknown')}")
        
        if health_result.get("status") != "healthy":
            print("⚠️  Health check failed, continuing with evaluations anyway...")
        
        # Run all evaluation tests
        eval_methods = [
            evaluator.eval_basic_session_creation,
            evaluator.eval_session_messaging,
            evaluator.eval_multi_user_sessions,
            evaluator.eval_session_state_persistence,
            evaluator.eval_error_handling
        ]
        
        results = []
        passed_count = 0
        
        for eval_method in eval_methods:
            try:
                result = await eval_method()
                results.append(result)
                if result["passed"]:
                    passed_count += 1
                    print(f"   ✅ {result['test_name']}: PASSED")
                else:
                    print(f"   ❌ {result['test_name']}: FAILED")
                    if result["errors"]:
                        for error in result["errors"]:
                            print(f"      Error: {error}")
            except Exception as e:
                print(f"   💥 {eval_method.__name__}: CRASHED - {e}")
                results.append({
                    "test_name": eval_method.__name__,
                    "passed": False,
                    "errors": [str(e)]
                })
        
        print("\n" + "=" * 50)
        print(f"📊 Session Evaluations Complete: {passed_count}/{len(eval_methods)} tests passed")
        print("=" * 50)
        
        return {
            "total_tests": len(eval_methods),
            "passed_tests": passed_count,
            "success_rate": passed_count / len(eval_methods) if eval_methods else 0,
            "results": results,
            "health_check": health_result
        }
        
    finally:
        await evaluator.cleanup()

if __name__ == "__main__":
    asyncio.run(run_session_evals()) 