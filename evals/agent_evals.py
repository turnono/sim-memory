#!/usr/bin/env python3
"""
Agent Behavior Evaluations
Tests for agent intelligence, conversation quality, and simulation guidance.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass
import time
import re
from datetime import datetime
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import session service functions directly
from sim_guide.services.session_service import (
    create_session,
    send_message,
    delete_session,
)


@dataclass
class EvalScenario:
    """Represents a simulation scenario for evaluation."""

    name: str
    description: str
    user_queries: List[str]
    expected_topics: List[str]  # Topics the agent should address
    complexity_level: str  # "basic", "intermediate", "advanced"


class AgentBehaviorEvals:
    """Evaluation suite for agent behavior and response quality."""

    def __init__(self):
        self.test_user_id = "agent_eval_user"
        self.created_sessions = []
        self.scenarios = self._create_scenarios()

    def _create_scenarios(self) -> List[EvalScenario]:
        """Create evaluation scenarios for different life guidance contexts."""
        return [
            EvalScenario(
                name="young_career_guidance",
                description="Young person needs help with career direction and starting their professional life",
                user_queries=[
                    "Hi, I'm new to the working world. Can you help me get started with my career?",
                    "What do I need to do first to build a successful career?",
                    "I don't understand how to navigate the job market. Can you guide me?",
                ],
                expected_topics=[
                    "career",
                    "job",
                    "professional",
                    "skills",
                    "networking",
                    "goals",
                ],
                complexity_level="basic",
            ),
            EvalScenario(
                name="relationship_optimization",
                description="Experienced person wants to improve their relationships and social connections",
                user_queries=[
                    "I need to improve my relationships for better personal fulfillment",
                    "How can I strengthen my connections with family and friends?",
                    "What's the best approach for building meaningful relationships?",
                ],
                expected_topics=[
                    "relationships",
                    "family",
                    "friends",
                    "communication",
                    "social",
                ],
                complexity_level="advanced",
            ),
            EvalScenario(
                name="personal_growth_challenges",
                description="User encountering obstacles in personal development and needs guidance",
                user_queries=[
                    "I keep struggling with personal growth and self-improvement",
                    "I'm facing challenges I don't know how to overcome",
                    "How do I develop better habits and break bad patterns?",
                ],
                expected_topics=[
                    "growth",
                    "development",
                    "habits",
                    "challenges",
                    "improvement",
                ],
                complexity_level="intermediate",
            ),
            EvalScenario(
                name="life_balance_analysis",
                description="User needs help achieving work-life balance and overall wellness",
                user_queries=[
                    "How do I achieve better work-life balance?",
                    "What should I focus on for overall life satisfaction?",
                    "Can you help me understand how to prioritize different life areas?",
                ],
                expected_topics=[
                    "balance",
                    "wellness",
                    "priorities",
                    "health",
                    "lifestyle",
                ],
                complexity_level="intermediate",
            ),
            EvalScenario(
                name="life_optimization_workflow",
                description="User wants to optimize their daily routines and life systems",
                user_queries=[
                    "How can I make my daily life more efficient and fulfilling?",
                    "What are the best practices for organizing my life effectively?",
                    "Can you suggest ways to optimize my routines and habits?",
                ],
                expected_topics=[
                    "efficiency",
                    "routines",
                    "habits",
                    "organization",
                    "optimization",
                ],
                complexity_level="advanced",
            ),
        ]

    async def cleanup(self):
        """Clean up all test sessions."""
        for user_id, session_id in self.created_sessions:
            try:
                await delete_session(user_id, session_id)
                print(f"🗑️  Cleaned up session {session_id} for user {user_id}")
            except Exception as e:
                print(f"⚠️  Failed to cleanup session {session_id}: {e}")
        self.created_sessions.clear()

    async def eval_scenario_responses(self, scenario: EvalScenario) -> Dict[str, Any]:
        """Evaluate agent responses for a specific scenario."""
        print(f"\n🎯 Evaluating Scenario: {scenario.name}")

        results = {
            "scenario_name": scenario.name,
            "passed": False,
            "details": {},
            "metrics": {},
            "errors": [],
        }

        try:
            # Create session for this scenario - using correct function signature
            session_info = await create_session(
                user_id=self.test_user_id,
                session_context={
                    "scenario": scenario.name,
                    "complexity": scenario.complexity_level,
                },
            )
            session_id = session_info["session_id"]
            self.created_sessions.append((self.test_user_id, session_id))

            # Send messages and collect responses
            conversation = []
            response_times = []

            for query in scenario.user_queries:
                start_time = time.time()
                response = await send_message(self.test_user_id, session_id, query)
                response_time = time.time() - start_time

                conversation.append(
                    {
                        "user": query,
                        "agent": response["agent_response"],
                        "status": response["status"],
                        "response_time": response_time,
                    }
                )
                response_times.append(response_time)

            # Analyze responses for topic coverage
            topic_coverage = self.analyze_topic_coverage(
                conversation, scenario.expected_topics
            )

            # Calculate quality metrics
            quality_score = self.calculate_quality_score(conversation, scenario)

            # Determine if scenario passed
            results["passed"] = (
                all(turn["status"] == "success" for turn in conversation)
                and topic_coverage >= 0.5  # At least 50% topic coverage
                and quality_score >= 0.6  # At least 60% quality score
            )

            results["details"] = {
                "conversation": conversation,
                "topic_coverage": topic_coverage,
                "covered_topics": self.get_covered_topics(
                    conversation, scenario.expected_topics
                ),
                "session_id": session_id,
            }
            results["metrics"] = {
                "avg_response_time": sum(response_times) / len(response_times),
                "total_turns": len(conversation),
                "topic_coverage": topic_coverage,
                "quality_score": quality_score,
            }

        except Exception as e:
            results["errors"].append(str(e))

        return results

    def analyze_topic_coverage(
        self, conversation: List[Dict], expected_topics: List[str]
    ) -> float:
        """Analyze how well the conversation covers expected topics."""
        if not expected_topics:
            return 1.0

        # Combine all agent responses
        all_responses = " ".join([turn["agent"].lower() for turn in conversation])

        # Count how many expected topics are mentioned
        topics_covered = 0
        for topic in expected_topics:
            if topic.lower() in all_responses:
                topics_covered += 1

        return topics_covered / len(expected_topics)

    def get_covered_topics(
        self, conversation: List[Dict], expected_topics: List[str]
    ) -> List[str]:
        """Get list of topics that were actually covered."""
        all_responses = " ".join([turn["agent"].lower() for turn in conversation])
        covered = []

        for topic in expected_topics:
            if topic.lower() in all_responses:
                covered.append(topic)

        return covered

    def calculate_quality_score(
        self, conversation: List[Dict], scenario: EvalScenario
    ) -> float:
        """Calculate overall quality score for the conversation."""
        if not conversation:
            return 0.0

        # Response length score (prefer substantial responses)
        avg_length = sum(len(turn["agent"]) for turn in conversation) / len(
            conversation
        )
        length_score = min(avg_length / 200, 1.0)  # Target ~200 chars, max 1.0

        # Success rate score
        success_rate = sum(
            1 for turn in conversation if turn["status"] == "success"
        ) / len(conversation)

        # Helpfulness score (look for helpful keywords)
        helpful_keywords = [
            "help",
            "can",
            "will",
            "let me",
            "i'll",
            "here's",
            "try",
            "consider",
        ]
        all_responses = " ".join([turn["agent"].lower() for turn in conversation])
        helpful_mentions = sum(
            1 for keyword in helpful_keywords if keyword in all_responses
        )
        helpful_score = min(helpful_mentions / 3, 1.0)  # Target 3+ helpful phrases

        # Combined score
        return (length_score + success_rate + helpful_score) / 3

    async def eval_consistency_across_sessions(self) -> Dict[str, Any]:
        """Test response consistency across multiple sessions."""
        print("\n🔄 Evaluating: Response Consistency")

        results = {
            "test_name": "response_consistency",
            "passed": False,
            "details": {},
            "errors": [],
        }

        try:
            test_message = "Hello, I need help with starting a simulation"
            responses = []

            # Create multiple sessions and ask the same question
            for i in range(3):
                user_id = f"{self.test_user_id}_{i}"
                session_info = await create_session(
                    user_id=user_id, session_context={"test_consistency": True}
                )
                session_id = session_info["session_id"]
                self.created_sessions.append((user_id, session_id))

                response = await send_message(user_id, session_id, test_message)
                responses.append(response["agent_response"])

            # Analyze consistency
            response_lengths = [len(r) for r in responses]
            avg_length = sum(response_lengths) / len(response_lengths)
            length_variance = sum(
                (l - avg_length) ** 2 for l in response_lengths
            ) / len(response_lengths)

            # Check for similar content (keywords)
            common_words = set()
            for response in responses:
                words = set(response.lower().split())
                if not common_words:
                    common_words = words
                else:
                    common_words &= words

            # Evaluate consistency
            length_consistent = length_variance < (
                avg_length * 0.5
            )  # Length variance < 50% of avg
            content_consistent = len(common_words) >= 3  # At least 3 common words

            results["passed"] = length_consistent and content_consistent
            results["details"] = {
                "responses": responses,
                "avg_length": avg_length,
                "length_variance": length_variance,
                "common_words": list(common_words),
                "length_consistent": length_consistent,
                "content_consistent": content_consistent,
            }

        except Exception as e:
            results["errors"].append(str(e))

        return results


async def run_agent_evals():
    """Run all agent behavior evaluations."""
    print("🤖 Starting Agent Behavior Evaluations")
    print("=" * 60)

    evaluator = AgentBehaviorEvals()

    try:
        results = []

        # Run scenario evaluations
        for scenario in evaluator.scenarios:
            result = await evaluator.eval_scenario_responses(scenario)
            results.append(result)

        # Run consistency test
        consistency_result = await evaluator.eval_consistency_across_sessions()
        results.append(consistency_result)

        # Summary
        print("\n" + "=" * 60)
        print("📊 Agent Behavior Evaluation Summary")
        print("=" * 60)

        passed = sum(1 for r in results if r["passed"])
        total = len(results)

        for result in results:
            status = "✅ PASS" if result["passed"] else "❌ FAIL"
            test_name = result.get("scenario_name", result.get("test_name", "unknown"))
            print(f"  {test_name}: {status}")

            if result.get("metrics"):
                metrics = result["metrics"]
                print(f"    Quality Score: {metrics.get('quality_score', 0):.2f}")
                print(f"    Topic Coverage: {metrics.get('topic_coverage', 0):.2f}")
                print(
                    f"    Avg Response Time: {metrics.get('avg_response_time', 0):.2f}s"
                )

            if result.get("errors"):
                for error in result["errors"]:
                    print(f"    Error: {error}")

        print(f"\nResults: {passed}/{total} tests passed")

        if passed == total:
            print("🎉 All agent behavior evaluations passed!")
        else:
            print(f"⚠️  {total - passed} evaluation(s) failed")

        return results

    finally:
        # Cleanup
        await evaluator.cleanup()


if __name__ == "__main__":
    asyncio.run(run_agent_evals())
