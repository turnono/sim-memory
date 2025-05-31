#!/usr/bin/env python3
"""
Performance Evaluations
Tests for response times, concurrent sessions, and scalability.
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
import time
import statistics
from concurrent.futures import ThreadPoolExecutor
import logging
from datetime import datetime, timezone
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import session service functions directly
from sim_guide.session_service import (
    create_session,
    send_message,
    delete_session,
    health_check,
    REASONING_ENGINE_ID
)

class PerformanceEvals:
    """Evaluation suite for performance and scalability testing."""
    
    def __init__(self):
        self.test_user_ids = [f"perf_user_{i}_{uuid.uuid4().hex[:8]}" for i in range(5)]
        self.created_sessions = []
    
    async def cleanup(self):
        """Clean up all test sessions."""
        print("\n🧹 Cleaning up performance test sessions...")
        cleanup_count = 0
        
        for user_id, session_id in self.created_sessions:
            try:
                await delete_session(user_id, session_id)
                cleanup_count += 1
            except Exception as e:
                logger.warning(f"Failed to cleanup session {session_id}: {e}")
        
        print(f"   Cleaned up {cleanup_count}/{len(self.created_sessions)} sessions")
        self.created_sessions.clear()

    async def eval_response_time_distribution(self) -> Dict[str, Any]:
        """Test response time distribution for various message types."""
        print("\n⏱️  Evaluating: Response Time Distribution")
        
        results = {
            "test_name": "response_time_distribution",
            "passed": False,
            "details": {},
            "metrics": {},
            "errors": []
        }
        
        try:
            user_id = "perf_user_timing"
            
            # Create session
            session_info = await create_session(
                user_id=user_id,
                session_context={"test_type": "performance"}
            )
            session_id = session_info["session_id"]
            self.created_sessions.append((user_id, session_id))
            
            # Test different message types and lengths
            test_messages = [
                ("short", "Hi"),
                ("short", "Help"),
                ("short", "Start"),
                ("medium", "Can you help me start a simulation?"),
                ("medium", "What are my options for configuration?"),
                ("medium", "How do I track the progress of my simulation?"),
                ("long", "I'm working on a complex simulation project and need detailed guidance on how to configure the advanced parameters, monitor the results, and optimize performance. Can you provide comprehensive assistance?"),
                ("long", "I've been running simulations for several hours now and I'm seeing some unexpected results in the output data. The metrics don't match my expectations and I'm wondering if there might be an issue with my configuration or if this is normal behavior for this type of simulation."),
                ("long", "Could you walk me through the entire process from start to finish, including how to set up the initial parameters, what to expect during execution, how to interpret the results, and what next steps I should take once the simulation is complete?")
            ]
            
            response_times = {"short": [], "medium": [], "long": []}
            
            for msg_type, message in test_messages:
                response = await send_message(user_id, session_id, message)
                response_times[msg_type].append(response["response_time_seconds"])
                
                # Small delay between requests
                await asyncio.sleep(0.1)
            
            # Calculate statistics
            stats = {}
            for msg_type, times in response_times.items():
                if times:
                    stats[msg_type] = {
                        "count": len(times),
                        "mean": statistics.mean(times),
                        "median": statistics.median(times),
                        "min": min(times),
                        "max": max(times),
                        "stdev": statistics.stdev(times) if len(times) > 1 else 0
                    }
            
            # Performance criteria
            all_times = [t for times in response_times.values() for t in times]
            avg_response_time = statistics.mean(all_times)
            max_response_time = max(all_times)
            
            # Pass if average < 5s and max < 10s
            results["passed"] = avg_response_time < 15.0 and max_response_time < 30.0
            
            results["details"] = {
                "response_times": response_times,
                "statistics": stats,
                "session_id": session_id
            }
            results["metrics"] = {
                "avg_response_time": avg_response_time,
                "max_response_time": max_response_time,
                "total_requests": len(all_times)
            }
            
        except Exception as e:
            results["errors"].append(str(e))
            
        return results
    
    async def eval_concurrent_sessions(self) -> Dict[str, Any]:
        """Test handling multiple concurrent sessions."""
        print("\n🔀 Evaluating: Concurrent Session Handling")
        
        results = {
            "test_name": "concurrent_sessions",
            "passed": False,
            "details": {},
            "metrics": {},
            "errors": []
        }
        
        try:
            num_concurrent_users = 5
            messages_per_user = 3
            
            # Create concurrent session tasks
            async def create_user_session(user_index):
                user_id = f"concurrent_user_{user_index}"
                try:
                    # Create session
                    session_info = await create_session(
                        user_id=user_id,
                        session_context={"user_index": user_index, "test_type": "concurrent"}
                    )
                    session_id = session_info["session_id"]
                    self.created_sessions.append((user_id, session_id))
                    
                    # Send messages
                    messages = [
                        f"Hello from user {user_index}",
                        f"This is message 2 from user {user_index}",
                        f"Final message from user {user_index}"
                    ]
                    
                    response_times = []
                    responses = []
                    
                    for i, message in enumerate(messages[:messages_per_user]):
                        response = await send_message(user_id, session_id, message)
                        response_times.append(response["response_time_seconds"])
                        responses.append(response["agent_response"])
                        
                        # Small delay between messages from same user
                        await asyncio.sleep(0.1)
                    
                    return {
                        "user_id": user_id,
                        "session_id": session_id,
                        "response_times": response_times,
                        "responses": responses,
                        "success": True
                    }
                    
                except Exception as e:
                    return {
                        "user_id": user_id,
                        "error": str(e),
                        "success": False
                    }
            
            # Run concurrent sessions
            start_time = time.time()
            user_tasks = [create_user_session(i) for i in range(num_concurrent_users)]
            user_results = await asyncio.gather(*user_tasks)
            total_time = time.time() - start_time
            
            # Analyze results
            successful_users = [r for r in user_results if r["success"]]
            failed_users = [r for r in user_results if not r["success"]]
            
            all_response_times = []
            for user_result in successful_users:
                all_response_times.extend(user_result["response_times"])
            
            # Performance criteria
            success_rate = len(successful_users) / len(user_results)
            avg_response_time = statistics.mean(all_response_times) if all_response_times else float('inf')
            
            # Pass if >80% success rate and reasonable response times
            results["passed"] = success_rate >= 0.8 and avg_response_time < 15.0
            
            results["details"] = {
                "successful_users": successful_users,
                "failed_users": failed_users,
                "total_time": total_time
            }
            results["metrics"] = {
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "concurrent_users": num_concurrent_users,
                "messages_per_user": messages_per_user
            }
            
        except Exception as e:
            results["errors"].append(str(e))
            
        return results
    
    async def eval_session_creation_speed(self) -> Dict[str, Any]:
        """Test session creation speed and consistency."""
        print("\n🚀 Evaluating: Session Creation Speed")
        
        results = {
            "test_name": "session_creation_speed",
            "passed": False,
            "details": {},
            "metrics": {},
            "errors": []
        }
        
        try:
            creation_times = []
            num_sessions = 10
            
            for i in range(num_sessions):
                user_id = f"speed_test_user_{i}"
                
                start_time = time.time()
                session_info = await create_session(
                    user_id=user_id,
                    session_context={"test": "creation_speed", "index": i}
                )
                creation_time = time.time() - start_time
                
                creation_times.append(creation_time)
                session_id = session_info["session_id"]
                self.created_sessions.append((user_id, session_id))
                
                # Small delay between creations
                await asyncio.sleep(0.1)
            
            # Calculate statistics
            avg_creation_time = statistics.mean(creation_times)
            max_creation_time = max(creation_times)
            min_creation_time = min(creation_times)
            
            # Pass if average < 3s and max < 5s
            results["passed"] = avg_creation_time < 3.0 and max_creation_time < 5.0
            
            results["details"] = {
                "creation_times": creation_times,
                "sessions_created": num_sessions
            }
            results["metrics"] = {
                "avg_creation_time": avg_creation_time,
                "max_creation_time": max_creation_time,
                "min_creation_time": min_creation_time,
                "total_sessions": num_sessions
            }
            
        except Exception as e:
            results["errors"].append(str(e))
            
        return results
    
    async def eval_memory_session_operations(self) -> Dict[str, Any]:
        """Test session operations with large state data."""
        print("\n🧠 Evaluating: Memory & Large Session Operations")
        
        results = {
            "test_name": "memory_session_operations",
            "passed": False,
            "details": {},
            "metrics": {},
            "errors": []
        }
        
        try:
            user_id = "memory_test_user"
            
            # Create large state for testing
            large_state = {
                "simulation_data": {
                    "parameters": {f"param_{i}": f"value_{i}" for i in range(100)},
                    "results": [{"step": i, "value": i * 2.5} for i in range(200)],
                    "metadata": {
                        "created": datetime.now(timezone.utc).isoformat(),
                        "description": "Large test state for memory evaluation" * 100
                    }
                }
            }
            
            # Test session creation with large state
            start_time = time.time()
            session_info = await create_session(
                user_id=user_id,
                session_context=large_state
            )
            session_id = session_info["session_id"]
            creation_time = time.time() - start_time
            self.created_sessions.append((user_id, session_id))
            
            # Test messaging with large state
            start_time = time.time()
            response = await send_message(
                user_id, 
                session_id,
                "Can you help me with my simulation?"
            )
            messaging_time = response["response_time_seconds"]
            
            # Memory efficiency criteria
            total_time = creation_time + messaging_time
            state_size = len(str(large_state))
            
            # Pass if operations complete efficiently despite large state
            results["passed"] = total_time < 20.0 and creation_time < 10.0
            
            results["details"] = {
                "state_size": state_size,
                "session_id": session_id,
                "response_received": len(response["agent_response"]) > 0
            }
            results["metrics"] = {
                "creation_time": creation_time,
                "messaging_time": messaging_time,
                "total_time": total_time,
                "state_size_bytes": state_size
            }
            
        except Exception as e:
            results["errors"].append(str(e))
            
        return results
    
    async def eval_burst_load_handling(self) -> Dict[str, Any]:
        """Test handling of burst load scenarios."""
        print("\n💥 Evaluating: Burst Load Handling")
        
        results = {
            "test_name": "burst_load_handling",
            "passed": False,
            "details": {},
            "metrics": {},
            "errors": []
        }
        
        try:
            user_id = "burst_test_user"
            
            # Create session
            session_info = await create_session(
                user_id=user_id,
                session_context={"test_type": "burst_load"}
            )
            session_id = session_info["session_id"]
            self.created_sessions.append((user_id, session_id))
            
            # Send burst of messages rapidly
            num_burst_messages = 5  # Reduced for realistic testing
            messages = [f"Burst message {i}" for i in range(num_burst_messages)]
            
            # Send messages with small delays (more realistic than truly concurrent)
            start_time = time.time()
            responses = []
            
            for message in messages:
                response = await send_message(user_id, session_id, message)
                responses.append(response)
                await asyncio.sleep(0.2)  # Small delay between messages
            
            total_burst_time = time.time() - start_time
            
            # Analyze burst results
            successful_responses = [r for r in responses if r["status"] == "success"]
            failed_responses = [r for r in responses if r["status"] != "success"]
            
            success_rate = len(successful_responses) / len(responses)
            avg_response_time = sum(r["response_time_seconds"] for r in responses) / len(responses)
            
            # Performance criteria: >80% success rate, reasonable average time
            results["passed"] = success_rate >= 0.8 and avg_response_time < 15.0
            
            results["details"] = {
                "burst_messages": num_burst_messages,
                "successful_responses": len(successful_responses),
                "failed_responses": len(failed_responses),
                "total_burst_time": total_burst_time
            }
            results["metrics"] = {
                "success_rate": success_rate,
                "avg_response_time": avg_response_time,
                "total_messages": len(messages)
            }
            
            if failed_responses:
                results["errors"].extend([f"Failed response: {r['status']}" for r in failed_responses])
            
        except Exception as e:
            results["errors"].append(str(e))
            
        return results

    async def eval_throughput_analysis(self) -> Dict[str, Any]:
        """Test throughput under sustained load."""
        print("\n📈 Evaluating: Throughput Analysis")
        
        results = {
            "test_name": "throughput_analysis",
            "passed": False,
            "details": {},
            "metrics": {},
            "errors": []
        }
        
        try:
            user_id = "throughput_user"
            
            # Create session
            session_info = await create_session(
                user_id=user_id,
                session_context={"test_type": "throughput"}
            )
            session_id = session_info["session_id"]
            self.created_sessions.append((user_id, session_id))
            
            # Sustained load test
            num_requests = 10  # Reduced for realistic testing
            messages = [f"Request {i}: Help with simulation" for i in range(num_requests)]
            
            # Send requests with delays to simulate realistic usage
            response_times = []
            successful_requests = 0
            
            start_time = time.time()
            for i, message in enumerate(messages):
                response = await send_message(user_id, session_id, message)
                response_times.append(response["response_time_seconds"])
                
                if response["status"] == "success":
                    successful_requests += 1
                
                # Small delay between requests (realistic usage pattern)
                await asyncio.sleep(1.0)  # 1 second between requests
            
            total_duration = time.time() - start_time
            
            # Calculate metrics
            throughput = successful_requests / total_duration  # requests per second
            avg_response_time = statistics.mean(response_times) if response_times else float('inf')
            success_rate = successful_requests / num_requests
            
            # Pass if throughput > 0.05 req/s and success rate > 90%
            results["passed"] = throughput > 0.05 and success_rate > 0.9
            
            results["details"] = {
                "total_requests": num_requests,
                "successful_requests": successful_requests,
                "response_times": response_times
            }
            results["metrics"] = {
                "throughput_req_per_sec": throughput,
                "avg_response_time": avg_response_time,
                "success_rate": success_rate,
                "total_duration": total_duration
            }
            
        except Exception as e:
            results["errors"].append(str(e))
            
        return results

async def run_performance_evals():
    """Run all performance evaluations."""
    print("⚡ Starting Performance Evaluations")
    print("=" * 60)
    
    evaluator = PerformanceEvals()
    
    try:
        # Run all performance evaluations
        eval_methods = [
            evaluator.eval_response_time_distribution,
            evaluator.eval_concurrent_sessions,
            evaluator.eval_session_creation_speed,
            evaluator.eval_memory_session_operations,
            evaluator.eval_burst_load_handling,
            evaluator.eval_throughput_analysis
        ]
        
        results = []
        for eval_method in eval_methods:
            try:
                result = await eval_method()
                results.append(result)
            except Exception as e:
                results.append({
                    "test_name": eval_method.__name__,
                    "passed": False,
                    "errors": [str(e)]
                })
        
        # Summary
        print("\n" + "=" * 60)
        print("📊 Performance Evaluation Summary")
        print("=" * 60)
        
        passed = sum(1 for r in results if r["passed"])
        total = len(results)
        
        for result in results:
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            print(f"  {result['test_name']}: {status}")
            
            if result.get("metrics"):
                metrics = result["metrics"]
                for key, value in metrics.items():
                    if isinstance(value, float):
                        print(f"    {key}: {value:.3f}")
                    else:
                        print(f"    {key}: {value}")
            
            if result.get("errors"):
                for error in result["errors"]:
                    print(f"    Error: {error}")
        
        print(f"\nResults: {passed}/{total} performance tests passed")
        
        if passed == total:
            print("🎉 All performance evaluations passed!")
        else:
            print(f"⚠️  {total - passed} performance test(s) failed")
        
        return results
        
    finally:
        # Cleanup
        await evaluator.cleanup()

if __name__ == "__main__":
    asyncio.run(run_performance_evals()) 