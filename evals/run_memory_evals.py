#!/usr/bin/env python3
"""
Memory Evaluations Runner

Runs comprehensive memory system evaluations in the correct order:
1. Core memory flow test (basic functionality) 
2. Memory integration tests (comprehensive)
3. Legacy memory tests (compatibility)

Focuses on the new ADK-compliant memory architecture.
"""

import sys
import os
import asyncio
import time
from datetime import datetime

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import our new memory tests
from memory_core_flow_test import test_core_memory_flow
from memory_integration_evals import run_memory_integration_evals

# Import legacy tests for compatibility
try:
    from memory_behavior_evals import run_all_memory_tests
    legacy_behavior_available = True
except ImportError:
    legacy_behavior_available = False

try:
    from rag_memory_evals import run_rag_memory_evals
    legacy_rag_available = True
except ImportError:
    legacy_rag_available = False


async def run_memory_evaluations():
    """Run all memory evaluations in order of priority"""
    print("🧠 MEMORY SYSTEM EVALUATION SUITE")
    print("=" * 80)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    total_start_time = time.time()
    results = {
        "core_flow": None,
        "integration": None,
        "legacy_behavior": None,
        "legacy_rag": None
    }
    
    # === PRIORITY 1: Core Memory Flow ===
    print("🎯 PRIORITY 1: Core Memory Flow Test")
    print("-" * 50)
    try:
        start_time = time.time()
        core_success = await test_core_memory_flow()
        duration = time.time() - start_time
        
        results["core_flow"] = {
            "success": core_success,
            "duration": duration,
            "status": "PASSED" if core_success else "FAILED"
        }
        
        print(f"⏱️  Duration: {duration:.1f}s")
        if core_success:
            print("✅ Core memory flow: FUNCTIONAL")
        else:
            print("❌ Core memory flow: BROKEN")
            
    except Exception as e:
        print(f"💥 Core memory flow test crashed: {e}")
        results["core_flow"] = {
            "success": False,
            "duration": 0,
            "status": "CRASHED",
            "error": str(e)
        }
    
    print("\n" + "=" * 80)
    
    # === PRIORITY 2: Memory Integration Tests ===
    print("🔧 PRIORITY 2: Memory Integration Tests")
    print("-" * 50)
    try:
        start_time = time.time()
        integration_results = await run_memory_integration_evals()
        duration = time.time() - start_time
        
        integration_success = integration_results["summary"]["all_passed"]
        results["integration"] = {
            "success": integration_success,
            "duration": duration,
            "status": "PASSED" if integration_success else "FAILED",
            "details": integration_results["summary"]
        }
        
        print(f"⏱️  Duration: {duration:.1f}s")
        
    except Exception as e:
        print(f"💥 Memory integration tests crashed: {e}")
        results["integration"] = {
            "success": False,
            "duration": 0,
            "status": "CRASHED", 
            "error": str(e)
        }
    
    print("\n" + "=" * 80)
    
    # === PRIORITY 3: Legacy Behavior Tests ===
    if legacy_behavior_available:
        print("📜 PRIORITY 3: Legacy Behavior Tests")
        print("-" * 50)
        try:
            start_time = time.time()
            run_all_memory_tests()  # This prints its own output
            duration = time.time() - start_time
            
            results["legacy_behavior"] = {
                "success": True,  # Assumes success if no exception
                "duration": duration,
                "status": "PASSED"
            }
            
            print(f"⏱️  Duration: {duration:.1f}s")
            
        except Exception as e:
            print(f"💥 Legacy behavior tests crashed: {e}")
            results["legacy_behavior"] = {
                "success": False,
                "duration": 0,
                "status": "CRASHED",
                "error": str(e)
            }
    else:
        print("📜 PRIORITY 3: Legacy Behavior Tests - SKIPPED (not available)")
        results["legacy_behavior"] = {"status": "SKIPPED"}
    
    print("\n" + "=" * 80)
    
    # === PRIORITY 4: Legacy RAG Tests ===
    if legacy_rag_available:
        print("🗃️ PRIORITY 4: Legacy RAG Memory Tests")
        print("-" * 50)
        try:
            start_time = time.time()
            rag_results = await run_rag_memory_evals()
            duration = time.time() - start_time
            
            rag_success = rag_results.get("overall_success", False)
            results["legacy_rag"] = {
                "success": rag_success,
                "duration": duration,
                "status": "PASSED" if rag_success else "FAILED"
            }
            
            print(f"⏱️  Duration: {duration:.1f}s")
            
        except Exception as e:
            print(f"💥 Legacy RAG tests crashed: {e}")
            results["legacy_rag"] = {
                "success": False,
                "duration": 0,
                "status": "CRASHED",
                "error": str(e)
            }
    else:
        print("🗃️ PRIORITY 4: Legacy RAG Memory Tests - SKIPPED (not available)")
        results["legacy_rag"] = {"status": "SKIPPED"}
    
    # === FINAL SUMMARY ===
    total_duration = time.time() - total_start_time
    
    print("\n" + "=" * 80)
    print("📊 MEMORY EVALUATION FINAL SUMMARY")
    print("=" * 80)
    
    # Count successes
    test_statuses = []
    for test_name, result in results.items():
        if result and "status" in result:
            status = result["status"]
            duration = result.get("duration", 0)
            
            if status == "PASSED":
                icon = "✅"
            elif status == "FAILED":
                icon = "❌"
            elif status == "CRASHED":
                icon = "💥"
            else:
                icon = "⏭️"
            
            print(f"{icon} {test_name.replace('_', ' ').title()}: {status} ({duration:.1f}s)")
            test_statuses.append(status)
    
    passed_count = test_statuses.count("PASSED")
    failed_count = test_statuses.count("FAILED") + test_statuses.count("CRASHED")
    skipped_count = test_statuses.count("SKIPPED")
    
    print(f"\n📈 Results: {passed_count} PASSED, {failed_count} FAILED, {skipped_count} SKIPPED")
    print(f"⏱️  Total Duration: {total_duration:.1f}s")
    
    # Overall assessment
    core_working = results["core_flow"]["success"] if results["core_flow"] else False
    integration_working = results["integration"]["success"] if results["integration"] else False
    
    if core_working and integration_working:
        print("\n🎉 MEMORY SYSTEM STATUS: FULLY FUNCTIONAL")
        print("✨ The complete memory architecture is working correctly!")
        print("   - Session persistence ✅")
        print("   - Memory tools ✅") 
        print("   - Cross-session retrieval ✅")
        print("   - Memory service integration ✅")
        
    elif core_working:
        print("\n⚠️  MEMORY SYSTEM STATUS: BASIC FUNCTIONALITY")
        print("🔧 Core memory flow works, but some advanced features may have issues.")
        
    else:
        print("\n🚨 MEMORY SYSTEM STATUS: CRITICAL ISSUES")
        print("❌ Core memory functionality is not working correctly.")
        print("🔧 Priority: Fix core memory flow before proceeding.")
    
    print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return {
        "overall_status": "FUNCTIONAL" if (core_working and integration_working) else "ISSUES",
        "core_working": core_working,
        "integration_working": integration_working,
        "total_duration": total_duration,
        "detailed_results": results
    }


def run_memory_evals_sync():
    """Synchronous wrapper for memory evaluations"""
    return asyncio.run(run_memory_evaluations())


if __name__ == "__main__":
    asyncio.run(run_memory_evaluations()) 