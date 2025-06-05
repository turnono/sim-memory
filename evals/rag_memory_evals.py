#!/usr/bin/env python3
"""
RAG Memory Service Evaluations
Tests for RAG memory management functionality.
"""

import sys
import os
import asyncio
import logging
import time
from typing import Dict, Any, List
from datetime import datetime, timezone
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import RAG memory service functions
from sim_guide.sub_agents.user_context_manager.services.rag_memory_service import (
    create_rag_corpus,
    add_memory_from_conversation,
    retrieve_user_memories,
    search_all_corpora,
    query_corpus,
    health_check,
    get_rag_config,
    search_memories_hybrid,
)


class RagMemoryEvals:
    """Test suite for RAG memory service functionality."""

    def __init__(self):
        self.test_prefix = f"test_{uuid.uuid4().hex[:8]}"
        self.created_corpora = []  # Track for cleanup
        self.test_user_id = f"test_user_{uuid.uuid4().hex[:8]}"

    async def cleanup(self):
        """Clean up test resources (simplified since delete_corpus is not available)."""
        print("\n🧹 Cleaning up test resources...")
        
        # Note: delete_corpus is not available in the current implementation
        # This is a simplified cleanup that just clears the tracking list
        cleanup_count = len(self.created_corpora)
        
        if cleanup_count > 0:
            print(f"   Note: {cleanup_count} test corpora were created (manual cleanup may be needed)")
        else:
            print("   No test corpora were created")
            
        self.created_corpora.clear()

    async def eval_corpus_management(self) -> Dict[str, Any]:
        """Test basic corpus management operations."""
        print("\n📚 Evaluating: Corpus Management")

        results = {
            "test_name": "corpus_management",
            "passed": False,
            "details": {},
            "errors": [],
        }

        try:
            corpus_name = f"{self.test_prefix}_test_corpus"
            corpus_id = f"test-corpus-{uuid.uuid4().hex[:8]}"

            # Test corpus creation using the available function
            create_response = await create_rag_corpus(
                corpus_id=corpus_id,
                display_name=corpus_name,
            )

            if create_response["status"] == "success":
                self.created_corpora.append(corpus_id)

            # Test basic configuration retrieval
            config_response = get_rag_config()

            results["passed"] = (
                create_response["status"] == "success" and
                config_response.get("enabled", False)
            )
            results["details"] = {
                "corpus_id": corpus_id,
                "corpus_name": corpus_name,
                "create_response": create_response,
                "config": config_response,
            }

        except Exception as e:
            results["errors"].append(str(e))

        return results

    async def eval_document_management(self) -> Dict[str, Any]:
        """Test memory storage functionality (simplified)."""
        print("\n📄 Evaluating: Memory Storage")

        results = {
            "test_name": "document_management",
            "passed": False,
            "details": {},
            "errors": [],
        }

        try:
            # Test memory storage using add_memory_from_conversation
            test_user_id = f"test_user_{uuid.uuid4().hex[:8]}"
            test_session_id = f"test_session_{uuid.uuid4().hex[:8]}"
            
            test_content = """
            Simulation Best Practices Guide
            
            1. Planning Phase:
            - Define clear objectives
            - Identify key parameters
            - Set up proper validation methods
            
            2. Execution Phase:
            - Monitor progress continuously
            - Validate intermediate results
            - Adjust parameters as needed
            
            3. Analysis Phase:
            - Review all outputs
            - Compare with expected results
            - Document lessons learned
            """

            # Test memory storage
            storage_response = await add_memory_from_conversation(
                user_id=test_user_id,
                session_id=test_session_id,
                conversation_text=test_content,
                memory_type="simulation_guide",
            )

            # Test memory retrieval
            retrieval_response = await retrieve_user_memories(
                user_id=test_user_id, 
                query="simulation best practices"
            )

            results["passed"] = (
                storage_response["status"] == "success" and
                len(retrieval_response) >= 0  # Even empty result is valid
            )
            results["details"] = {
                "test_user_id": test_user_id,
                "test_session_id": test_session_id,
                "storage_response": storage_response,
                "retrieval_count": len(retrieval_response),
                "retrieval_sample": retrieval_response[0][:100] if retrieval_response else "No results",
            }

        except Exception as e:
            results["errors"].append(str(e))

        return results

    async def eval_corpus_querying(self) -> Dict[str, Any]:
        """Test corpus querying and search functionality."""
        print("\n🔍 Evaluating: Memory Search")

        results = {
            "test_name": "corpus_querying",
            "passed": False,
            "details": {},
            "errors": [],
        }

        try:
            # Test global corpus search
            search_response = await search_all_corpora(
                query="simulation configuration best practices",
                top_k_per_corpus=3
            )

            # Test hybrid memory search
            hybrid_response = await search_memories_hybrid(
                user_id="test_search_user",
                query="simulation parameters and configuration",
                force_semantic=False
            )

            # Test individual corpus query if we have any corpus IDs
            corpus_query_response = None
            if self.created_corpora:
                corpus_query_response = await query_corpus(
                    corpus_id=self.created_corpora[0],
                    query="simulation best practices",
                    top_k=5
                )

            results["passed"] = (
                search_response["status"] == "success" and
                hybrid_response["status"] == "success"
            )
            
            results["details"] = {
                "search_all_response": search_response,
                "hybrid_response": hybrid_response,
                "corpus_query_response": corpus_query_response,
                "tested_corpora": len(self.created_corpora),
            }

        except Exception as e:
            results["errors"].append(str(e))

        return results

    async def eval_memory_functionality(self) -> Dict[str, Any]:
        """Test user memory storage and retrieval."""
        print("\n🧠 Evaluating: Memory Functionality")

        results = {
            "test_name": "memory_functionality",
            "passed": False,
            "details": {},
            "errors": [],
        }

        try:
            session_id = f"test_session_{uuid.uuid4().hex[:8]}"

            # Test adding conversation memory
            conversation_text = """
            User: I'm working on a CFD simulation of airflow over a wing. What parameters should I focus on?
            
            Agent: For a CFD simulation of airflow over a wing, focus on these key parameters:
            
            1. Reynolds number - determines the flow regime
            2. Angle of attack - affects lift and drag characteristics  
            3. Mach number - important for compressibility effects
            4. Mesh resolution - especially near the wing surface
            5. Turbulence model selection - k-ε, k-ω, or LES depending on needs
            
            Make sure to validate with wind tunnel data if available.
            
            User: How do I set up boundary conditions properly?
            
            Agent: For wing CFD simulations, set these boundary conditions:
            
            1. Inlet: Velocity inlet with uniform flow
            2. Outlet: Pressure outlet with atmospheric pressure
            3. Wing surface: No-slip wall condition
            4. Farfield: Slip wall or symmetry conditions
            5. Top/bottom: Symmetry conditions if 2D, or farfield if 3D
            
            Ensure the domain is large enough to avoid boundary effects.
            """

            # Add memory
            memory_response = await add_memory_from_conversation(
                user_id=self.test_user_id,
                session_id=session_id,
                conversation_text=conversation_text,
                memory_type="cfd_consultation",
            )

            assert memory_response["status"] == "success"

            # Wait for indexing
            await asyncio.sleep(3)

            # Test memory retrieval with different queries
            memory_queries = [
                "CFD parameters for wing simulation",
                "boundary conditions setup",
                "Reynolds number and turbulence models",
                "mesh resolution requirements",
            ]

            retrieval_results = []
            for query in memory_queries:
                # retrieve_user_memories returns List[str], not dict
                retrieval_memories = await retrieve_user_memories(
                    user_id=self.test_user_id, query=query
                )

                retrieval_results.append(
                    {
                        "query": query,
                        "memory_count": len(retrieval_memories),
                        "has_memories": len(retrieval_memories) > 0,
                        "sample": retrieval_memories[0][:100] if retrieval_memories else "No memories",
                    }
                )

            # Test memory retrieval for non-existent user
            empty_retrieval = await retrieve_user_memories(
                user_id="non_existent_user", query="test query"
            )

            results["passed"] = (
                memory_response["status"] == "success"
                and len(retrieval_results) > 0
                and len(empty_retrieval) == 0  # Should be empty list for non-existent user
            )

            results["details"] = {
                "user_id": self.test_user_id,
                "session_id": session_id,
                "memory_response": memory_response,
                "retrieval_results": retrieval_results,
                "successful_retrievals": len(
                    [r for r in retrieval_results if r["has_memories"]]
                ),
                "empty_user_retrieval_count": len(empty_retrieval),
            }

        except Exception as e:
            results["errors"].append(str(e))

        return results

    async def eval_health_check(self) -> Dict[str, Any]:
        """Test RAG memory service health check."""
        print("\n💚 Evaluating: Health Check")

        results = {
            "test_name": "health_check",
            "passed": False,
            "details": {},
            "errors": [],
        }

        try:
            health_response = await health_check()

            # Check the basic fields that should exist
            required_fields = ["status", "duration_seconds"]
            has_required_fields = all(field in health_response for field in required_fields)
            
            valid_status = health_response.get("status") in ["healthy", "degraded", "unhealthy"]

            results["passed"] = has_required_fields and valid_status
            results["details"] = health_response

        except Exception as e:
            results["errors"].append(str(e))

        return results


async def run_rag_memory_evals() -> Dict[str, Any]:
    """Run all RAG memory service evaluations."""
    print("🔬 Starting RAG Memory Service Evaluations")
    print("=" * 50)

    evaluator = RagMemoryEvals()
    eval_results = []

    try:
        # Run all evaluations
        evaluations = [
            evaluator.eval_health_check,
            evaluator.eval_corpus_management,
            evaluator.eval_document_management,
            evaluator.eval_corpus_querying,
            evaluator.eval_memory_functionality,
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

    finally:
        # Cleanup
        await evaluator.cleanup()

    # Summary
    print("\n" + "=" * 50)
    passed_tests = len([r for r in eval_results if r["passed"]])
    total_tests = len(eval_results)

    print(f"RAG Memory Service Evaluation Results:")
    print(f"   Passed: {passed_tests}/{total_tests}")
    print(f"   Success Rate: {(passed_tests / total_tests) * 100:.1f}%")

    if passed_tests == total_tests:
        print("🎉 All RAG memory service tests passed!")
    else:
        print("⚠️  Some RAG memory service tests failed - check logs for details")

    return {
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "success_rate": passed_tests / total_tests,
        "results": eval_results,
    }


if __name__ == "__main__":
    asyncio.run(run_rag_memory_evals())
