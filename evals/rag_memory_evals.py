#!/usr/bin/env python3
"""
RAG Memory Service Evaluations
Tests for RAG memory management functionality.
"""

import asyncio
import logging
import time
from typing import Dict, Any, List
from datetime import datetime, timezone
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import RAG memory service functions
from sim_guide.sub_agents.user_context_manager.services.rag_memory_service import (
    create_corpus,
    list_corpora,
    get_corpus,
    delete_corpus,
    upload_document_to_gcs,
    import_document_to_corpus,
    query_corpus,
    search_all_corpora,
    add_memory_from_conversation,
    retrieve_user_memories,
    health_check,
)


class RagMemoryEvals:
    """Test suite for RAG memory service functionality."""

    def __init__(self):
        self.test_prefix = f"test_{uuid.uuid4().hex[:8]}"
        self.created_corpora = []  # Track for cleanup
        self.test_user_id = f"test_user_{uuid.uuid4().hex[:8]}"

    async def cleanup(self):
        """Clean up test corpora."""
        print("\n🧹 Cleaning up test corpora...")
        cleanup_count = 0

        for corpus_id in self.created_corpora:
            try:
                await delete_corpus(corpus_id)
                cleanup_count += 1
            except Exception as e:
                logger.warning(f"Failed to cleanup corpus {corpus_id}: {e}")

        print(f"   Cleaned up {cleanup_count}/{len(self.created_corpora)} corpora")
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

            # Test corpus creation
            create_response = await create_corpus(
                display_name=corpus_name,
                description="Test corpus for evaluation",
                embedding_model="text-embedding-004",
            )

            assert create_response["status"] == "success"
            corpus_id = create_response["corpus_id"]
            self.created_corpora.append(corpus_id)

            # Test corpus retrieval
            get_response = await get_corpus(corpus_id)
            assert get_response["status"] == "success"
            assert get_response["display_name"] == corpus_name

            # Test corpus listing
            list_response = await list_corpora()
            assert list_response["status"] == "success"
            assert any(c["corpus_id"] == corpus_id for c in list_response["corpora"])

            results["passed"] = True
            results["details"] = {
                "corpus_id": corpus_id,
                "corpus_name": corpus_name,
                "create_response": create_response,
                "get_response": get_response,
                "total_corpora": list_response["count"],
            }

        except Exception as e:
            results["errors"].append(str(e))

        return results

    async def eval_document_management(self) -> Dict[str, Any]:
        """Test document upload and import functionality."""
        print("\n📄 Evaluating: Document Management")

        results = {
            "test_name": "document_management",
            "passed": False,
            "details": {},
            "errors": [],
        }

        try:
            # Create test corpus
            corpus_name = f"{self.test_prefix}_doc_corpus"
            corpus_response = await create_corpus(
                display_name=corpus_name,
                description="Test corpus for document evaluation",
            )

            assert corpus_response["status"] == "success"
            corpus_id = corpus_response["corpus_id"]
            self.created_corpora.append(corpus_id)

            # Create test document content
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

            # Test document upload to GCS
            upload_response = await upload_document_to_gcs(
                file_content=test_content.encode("utf-8"),
                file_name="test_simulation_guide.txt",
                content_type="text/plain",
            )

            assert upload_response["status"] == "success"
            gcs_uri = upload_response["gcs_uri"]

            # Test document import to corpus
            import_response = await import_document_to_corpus(
                corpus_id=corpus_id,
                gcs_uri=gcs_uri,
                display_name="Test Simulation Guide",
            )

            assert import_response["status"] == "success"

            # Wait a bit for indexing (in real usage this might take longer)
            await asyncio.sleep(2)

            results["passed"] = True
            results["details"] = {
                "corpus_id": corpus_id,
                "gcs_uri": gcs_uri,
                "upload_response": upload_response,
                "import_response": import_response,
                "document_size": upload_response["size_bytes"],
            }

        except Exception as e:
            results["errors"].append(str(e))

        return results

    async def eval_corpus_querying(self) -> Dict[str, Any]:
        """Test corpus querying and search functionality."""
        print("\n🔍 Evaluating: Corpus Querying")

        results = {
            "test_name": "corpus_querying",
            "passed": False,
            "details": {},
            "errors": [],
        }

        try:
            # Create test corpus with content
            corpus_name = f"{self.test_prefix}_query_corpus"
            corpus_response = await create_corpus(
                display_name=corpus_name, description="Test corpus for query evaluation"
            )

            assert corpus_response["status"] == "success"
            corpus_id = corpus_response["corpus_id"]
            self.created_corpora.append(corpus_id)

            # Upload simulation guidance content
            test_content = """
            Simulation Configuration Best Practices
            
            When configuring a simulation, follow these key principles:
            
            1. Parameter Selection:
            - Choose realistic parameter values based on domain knowledge
            - Use sensitivity analysis to identify critical parameters
            - Document all parameter choices and their rationale
            
            2. Validation Methods:
            - Compare results with analytical solutions when available
            - Use mesh convergence studies for spatial discretization
            - Verify energy conservation and mass balance
            
            3. Performance Optimization:
            - Profile your simulation to identify bottlenecks
            - Use appropriate time step sizes for stability
            - Consider parallel processing for large problems
            
            4. Result Interpretation:
            - Always visualize results before drawing conclusions
            - Check for physical reasonableness of outputs
            - Perform uncertainty quantification when possible
            """

            upload_response = await upload_document_to_gcs(
                file_content=test_content.encode("utf-8"),
                file_name="simulation_config_guide.txt",
                content_type="text/plain",
            )

            assert upload_response["status"] == "success"

            import_response = await import_document_to_corpus(
                corpus_id=corpus_id, gcs_uri=upload_response["gcs_uri"]
            )

            assert import_response["status"] == "success"

            # Wait for indexing
            await asyncio.sleep(3)

            # Test different types of queries
            test_queries = [
                "How do I choose simulation parameters?",
                "What are validation methods for simulations?",
                "Performance optimization techniques",
                "Result interpretation best practices",
            ]

            query_results = []
            for query in test_queries:
                query_response = await query_corpus(
                    corpus_id=corpus_id, query=query, top_k=5
                )

                if query_response["status"] == "success":
                    query_results.append(
                        {
                            "query": query,
                            "results_count": query_response["results_count"],
                            "has_results": len(query_response["results"]) > 0,
                        }
                    )

            # Test search all corpora
            search_response = await search_all_corpora(
                query="simulation best practices"
            )

            results["passed"] = (
                len(query_results) > 0 and search_response["status"] == "success"
            )
            results["details"] = {
                "corpus_id": corpus_id,
                "query_results": query_results,
                "search_all_response": search_response,
                "successful_queries": len(
                    [q for q in query_results if q["has_results"]]
                ),
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
                retrieval_response = await retrieve_user_memories(
                    user_id=self.test_user_id, query=query, top_k=3
                )

                if retrieval_response["status"] == "success":
                    retrieval_results.append(
                        {
                            "query": query,
                            "memory_count": retrieval_response["memory_count"],
                            "has_memories": len(retrieval_response["memories"]) > 0,
                        }
                    )

            # Test memory retrieval for non-existent user
            empty_retrieval = await retrieve_user_memories(
                user_id="non_existent_user", query="test query"
            )

            results["passed"] = (
                memory_response["status"] == "success"
                and len(retrieval_results) > 0
                and empty_retrieval["status"] == "success"
                and len(empty_retrieval["memories"]) == 0
            )

            results["details"] = {
                "user_id": self.test_user_id,
                "session_id": session_id,
                "memory_response": memory_response,
                "retrieval_results": retrieval_results,
                "successful_retrievals": len(
                    [r for r in retrieval_results if r["has_memories"]]
                ),
                "empty_user_test": empty_retrieval,
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

            assert health_response["status"] in ["healthy", "degraded"]
            assert "duration_seconds" in health_response
            assert "timestamp" in health_response
            assert "corpora_accessible" in health_response

            results["passed"] = health_response["status"] in ["healthy", "degraded"]
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
