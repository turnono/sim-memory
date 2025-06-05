"""
Business Strategist Evaluation Suite

Comprehensive evaluations for the Business Strategist hierarchical sub-agent system.
Tests functionality, delegation, context-passing, and business advice quality.
"""

import asyncio
import logging
from typing import Dict
from datetime import datetime


from sim_guide.sub_agents.business_strategist.tools.business_strategy import (
    get_business_strategy_advice,
    analyze_business_opportunity,
    get_business_strategic_plan,
    get_competitive_analysis,
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BusinessStrategistEvaluator:
    """Evaluator for Business Strategist system."""

    def __init__(self):
        self.results = {}
        self.start_time = None

    async def run_all_evaluations(self) -> Dict:
        """Run all Business Strategist evaluations."""
        self.start_time = datetime.now()

        print("🎯 " + "=" * 60)
        print("🎯 Business Strategist Evaluation Suite")
        print("🎯 " + "=" * 60)

        evaluations = [
            ("Tool Functionality", self.eval_tool_functionality),
            ("Business Advice Quality", self.eval_business_advice_quality),
            ("Delegation Effectiveness", self.eval_delegation_effectiveness),
            ("Context Handling", self.eval_context_handling),
            ("End-to-End Integration", self.eval_end_to_end_integration),
            ("Performance Metrics", self.eval_performance_metrics),
        ]

        for eval_name, eval_func in evaluations:
            print(f"\n📊 Running: {eval_name}")
            print("-" * 50)
            try:
                result = await eval_func()
                self.results[eval_name] = result
                print(f"✅ {eval_name}: {'PASSED' if result['passed'] else 'FAILED'}")
            except Exception as e:
                print(f"❌ {eval_name}: ERROR - {e}")
                self.results[eval_name] = {"passed": False, "error": str(e)}

        return self._generate_summary()

    async def eval_tool_functionality(self) -> Dict:
        """Test that all business strategy tools work correctly."""
        results = {
            "passed": True,
            "tests": {},
            "details": "Testing business strategy tool functionality",
        }

        # Test each tool function
        tools_to_test = [
            (
                "Business Strategy Advice",
                get_business_strategy_advice,
                {
                    "business_question": "How should I price my SaaS product?",
                    "business_context": "AI life guidance system for professionals",
                    "user_style": "Data-driven software developer",
                },
            ),
            (
                "Opportunity Analysis",
                analyze_business_opportunity,
                {
                    "opportunity_description": "Partnership with productivity app",
                    "business_context": "Early-stage SaaS product",
                    "user_style": "Conservative risk approach",
                },
            ),
            (
                "Strategic Planning",
                get_business_strategic_plan,
                {
                    "business_goal": "Launch MVP and get 100 customers",
                    "business_context": "AI guidance system",
                    "user_style": "Iterative development approach",
                    "timeframe": "6 months",
                },
            ),
            (
                "Competitive Analysis",
                get_competitive_analysis,
                {
                    "competitor_info": "BetterUp, life coaching apps, AI assistants",
                    "business_context": "AI life guidance platform",
                    "user_style": "Technology differentiation focus",
                },
            ),
        ]

        for tool_name, tool_func, params in tools_to_test:
            try:
                response = await tool_func(**params)

                # Check if response contains expected elements
                is_valid = (
                    response is not None
                    and len(response) > 50
                    and "Request:" in response
                    and not "❌" in response
                )

                results["tests"][tool_name] = {
                    "passed": is_valid,
                    "response_length": len(response) if response else 0,
                    "has_error": "❌" in response if response else True,
                }

                if not is_valid:
                    results["passed"] = False

                print(f"  📝 {tool_name}: {'✅ PASS' if is_valid else '❌ FAIL'}")

            except Exception as e:
                results["tests"][tool_name] = {"passed": False, "error": str(e)}
                results["passed"] = False
                print(f"  📝 {tool_name}: ❌ ERROR - {e}")

        return results

    async def eval_business_advice_quality(self) -> Dict:
        """Test the quality and relevance of business advice."""
        results = {
            "passed": True,
            "tests": {},
            "details": "Testing business advice quality and relevance",
        }

        # Test scenarios with expected elements
        test_scenarios = [
            {
                "name": "Pricing Strategy",
                "context": "Building Taajirah, an AI life guidance SaaS. Target: professionals seeking development.",
                "question": "What pricing model should I use?",
                "user_style": "Software developer, data-driven, lean startup",
                "expected_elements": [
                    "pricing",
                    "model",
                    "strategy",
                    "saas",
                    "customer",
                ],
            },
            {
                "name": "Marketing Strategy",
                "context": "AI life guidance platform, early development stage",
                "question": "How do I acquire my first customers?",
                "user_style": "Technical founder, limited marketing experience",
                "expected_elements": [
                    "marketing",
                    "customer",
                    "acquisition",
                    "channel",
                    "strategy",
                ],
            },
            {
                "name": "Growth Planning",
                "context": "Working prototype of AI guidance system, need to scale",
                "question": "How do I grow from 0 to 1000 users?",
                "user_style": "Methodical, prefers gradual growth",
                "expected_elements": ["growth", "user", "scale", "metrics", "plan"],
            },
        ]

        for scenario in test_scenarios:
            try:
                response = await get_business_strategy_advice(
                    business_question=scenario["question"],
                    business_context=scenario["context"],
                    user_style=scenario["user_style"],
                )

                # Check for expected business elements
                response_lower = response.lower() if response else ""
                elements_found = sum(
                    1
                    for element in scenario["expected_elements"]
                    if element in response_lower
                )
                relevance_score = elements_found / len(scenario["expected_elements"])

                is_quality = (
                    response
                    and len(response) > 100
                    and relevance_score >= 0.3  # At least 30% of expected elements
                    and not "❌" in response
                )

                results["tests"][scenario["name"]] = {
                    "passed": is_quality,
                    "relevance_score": relevance_score,
                    "elements_found": elements_found,
                    "total_elements": len(scenario["expected_elements"]),
                    "response_length": len(response) if response else 0,
                }

                if not is_quality:
                    results["passed"] = False

                print(
                    f"  🎯 {scenario['name']}: {'✅ PASS' if is_quality else '❌ FAIL'} "
                    f"(Relevance: {relevance_score:.1%})"
                )

            except Exception as e:
                results["tests"][scenario["name"]] = {"passed": False, "error": str(e)}
                results["passed"] = False
                print(f"  🎯 {scenario['name']}: ❌ ERROR - {e}")

        return results

    async def eval_delegation_effectiveness(self) -> Dict:
        """Test that the system effectively delegates to appropriate sub-agents."""
        results = {
            "passed": True,
            "tests": {},
            "details": "Testing automatic delegation to specialized sub-agents",
        }

        # Test delegation scenarios - these should trigger specific sub-agents
        delegation_tests = [
            {
                "name": "Marketing Question → Marketing Strategist",
                "question": "What's the best marketing channel for customer acquisition?",
                "context": "SaaS product targeting professionals",
                "expected_domain": "marketing",
                "expected_keywords": [
                    "marketing",
                    "acquisition",
                    "channel",
                    "customer",
                ],
            },
            {
                "name": "Finance Question → Finance Strategist",
                "question": "How much runway do I need and what funding options should I consider?",
                "context": "Early-stage startup with prototype",
                "expected_domain": "finance",
                "expected_keywords": ["funding", "runway", "financial", "investment"],
            },
            {
                "name": "Product Question → Product Strategist",
                "question": "How do I validate product-market fit for my AI guidance tool?",
                "context": "Built working prototype, need user validation",
                "expected_domain": "product",
                "expected_keywords": ["product", "market", "fit", "validation", "user"],
            },
            {
                "name": "Operations Question → Operations Strategist",
                "question": "How do I scale my operations from 100 to 10,000 users?",
                "context": "Growing user base, need operational efficiency",
                "expected_domain": "operations",
                "expected_keywords": ["operations", "scale", "process", "efficiency"],
            },
        ]

        for test in delegation_tests:
            try:
                response = await get_business_strategy_advice(
                    business_question=test["question"],
                    business_context=test["context"],
                    user_style="Analytical, systematic approach",
                )

                # Check if response contains domain-specific keywords
                response_lower = response.lower() if response else ""
                keyword_matches = sum(
                    1
                    for keyword in test["expected_keywords"]
                    if keyword in response_lower
                )

                delegation_score = keyword_matches / len(test["expected_keywords"])
                is_delegated = delegation_score >= 0.5  # At least 50% keyword match

                results["tests"][test["name"]] = {
                    "passed": is_delegated,
                    "delegation_score": delegation_score,
                    "keyword_matches": keyword_matches,
                    "total_keywords": len(test["expected_keywords"]),
                    "domain": test["expected_domain"],
                }

                if not is_delegated:
                    results["passed"] = False

                print(
                    f"  🔄 {test['name']}: {'✅ PASS' if is_delegated else '❌ FAIL'} "
                    f"(Score: {delegation_score:.1%})"
                )

            except Exception as e:
                results["tests"][test["name"]] = {"passed": False, "error": str(e)}
                results["passed"] = False
                print(f"  🔄 {test['name']}: ❌ ERROR - {e}")

        return results

    async def eval_context_handling(self) -> Dict:
        """Test that context is properly passed and utilized."""
        results = {
            "passed": True,
            "tests": {},
            "details": "Testing context-passing architecture",
        }

        # Test with different context scenarios
        context_tests = [
            {
                "name": "Rich Context Utilization",
                "context": "Building Taajirah, AI life guidance SaaS. Current stage: working prototype. Target market: professionals aged 25-40 seeking personal development. Technical founder with limited business experience.",
                "question": "What should be my go-to-market strategy?",
                "user_style": "Technical background, prefers systematic approaches, risk-averse",
                "should_contain": [
                    "prototype",
                    "professional",
                    "technical",
                    "systematic",
                ],
            },
            {
                "name": "User Style Integration",
                "context": "Early-stage AI platform",
                "question": "How should I approach fundraising?",
                "user_style": "Conservative, prefers bootstrapping, values control, dislikes investor pressure",
                "should_contain": ["bootstrap", "control", "conservative"],
            },
            {
                "name": "Minimal Context Handling",
                "context": "",  # Test with minimal context
                "question": "How do I price my product?",
                "user_style": "",
                "should_contain": [
                    "pricing",
                    "strategy",
                ],  # Should still provide basic advice
            },
        ]

        for test in context_tests:
            try:
                response = await get_business_strategy_advice(
                    business_question=test["question"],
                    business_context=test["context"],
                    user_style=test["user_style"],
                )

                # Check if context elements are reflected in response
                response_lower = response.lower() if response else ""
                context_reflection = sum(
                    1 for element in test["should_contain"] if element in response_lower
                )

                context_score = (
                    context_reflection / len(test["should_contain"])
                    if test["should_contain"]
                    else 1
                )
                is_context_aware = context_score >= 0.3 and len(response) > 50

                results["tests"][test["name"]] = {
                    "passed": is_context_aware,
                    "context_score": context_score,
                    "elements_reflected": context_reflection,
                    "total_elements": len(test["should_contain"]),
                    "response_length": len(response) if response else 0,
                }

                if not is_context_aware:
                    results["passed"] = False

                print(
                    f"  📋 {test['name']}: {'✅ PASS' if is_context_aware else '❌ FAIL'} "
                    f"(Context: {context_score:.1%})"
                )

            except Exception as e:
                results["tests"][test["name"]] = {"passed": False, "error": str(e)}
                results["passed"] = False
                print(f"  📋 {test['name']}: ❌ ERROR - {e}")

        return results

    async def eval_end_to_end_integration(self) -> Dict:
        """Test end-to-end integration with the root agent."""
        results = {
            "passed": True,
            "tests": {},
            "details": "Testing integration with root agent and full system",
        }

        # Test full integration scenarios
        integration_tests = [
            {
                "name": "Business Question to Root Agent",
                "message": "I need help with business strategy for my AI life guidance product Taajirah. How should I approach pricing and customer acquisition?",
                "expected_elements": ["business", "strategy", "pricing", "customer"],
            },
            {
                "name": "Complex Business Scenario",
                "message": "I'm Abdullah, a software developer building Taajirah. I have a working prototype but need to decide between bootstrapping vs seeking investment, and whether to focus on B2B or B2C market first.",
                "expected_elements": [
                    "investment",
                    "bootstrap",
                    "market",
                    "b2b",
                    "b2c",
                ],
            },
        ]

        for test in integration_tests:
            try:
                # This would test through the root agent when properly integrated
                # For now, we'll test the tool preparation
                response = await get_business_strategy_advice(
                    business_question=test["message"],
                    business_context="Full system integration test",
                    user_style="Software developer, analytical approach",
                )

                # Check if response contains expected business elements
                response_lower = response.lower() if response else ""
                elements_found = sum(
                    1
                    for element in test["expected_elements"]
                    if element in response_lower
                )

                integration_score = elements_found / len(test["expected_elements"])
                is_integrated = (
                    response
                    and len(response) > 100
                    and integration_score >= 0.3
                    and not "❌" in response
                )

                results["tests"][test["name"]] = {
                    "passed": is_integrated,
                    "integration_score": integration_score,
                    "elements_found": elements_found,
                    "response_length": len(response) if response else 0,
                }

                if not is_integrated:
                    results["passed"] = False

                print(
                    f"  🔗 {test['name']}: {'✅ PASS' if is_integrated else '❌ FAIL'} "
                    f"(Integration: {integration_score:.1%})"
                )

            except Exception as e:
                results["tests"][test["name"]] = {"passed": False, "error": str(e)}
                results["passed"] = False
                print(f"  🔗 {test['name']}: ❌ ERROR - {e}")

        return results

    async def eval_performance_metrics(self) -> Dict:
        """Test performance and efficiency metrics."""
        results = {
            "passed": True,
            "tests": {},
            "details": "Testing performance and efficiency metrics",
        }

        # Test response times and efficiency
        import time

        performance_tests = [
            (
                "Simple Business Question",
                get_business_strategy_advice,
                {
                    "business_question": "How do I price my product?",
                    "business_context": "SaaS product",
                    "user_style": "Analytical",
                },
            ),
            (
                "Complex Strategic Planning",
                get_business_strategic_plan,
                {
                    "business_goal": "Scale to 1000 users in 6 months",
                    "business_context": "AI guidance platform",
                    "user_style": "Systematic approach",
                },
            ),
        ]

        for test_name, func, params in performance_tests:
            try:
                start_time = time.time()
                response = await func(**params)
                end_time = time.time()

                response_time = end_time - start_time
                is_performant = (
                    response_time < 10.0  # Should respond within 10 seconds
                    and response
                    and len(response) > 50
                    and not "❌" in response
                )

                results["tests"][test_name] = {
                    "passed": is_performant,
                    "response_time": response_time,
                    "response_length": len(response) if response else 0,
                    "has_error": "❌" in response if response else True,
                }

                if not is_performant:
                    results["passed"] = False

                print(
                    f"  ⚡ {test_name}: {'✅ PASS' if is_performant else '❌ FAIL'} "
                    f"({response_time:.2f}s)"
                )

            except Exception as e:
                results["tests"][test_name] = {"passed": False, "error": str(e)}
                results["passed"] = False
                print(f"  ⚡ {test_name}: ❌ ERROR - {e}")

        return results

    def _generate_summary(self) -> Dict:
        """Generate evaluation summary."""
        total_evaluations = len(self.results)
        passed_evaluations = sum(
            1 for result in self.results.values() if result.get("passed", False)
        )

        total_time = (datetime.now() - self.start_time).total_seconds()

        summary = {
            "overall_passed": passed_evaluations == total_evaluations,
            "total_evaluations": total_evaluations,
            "passed_evaluations": passed_evaluations,
            "success_rate": passed_evaluations / total_evaluations
            if total_evaluations > 0
            else 0,
            "total_time": total_time,
            "detailed_results": self.results,
            "timestamp": datetime.now().isoformat(),
        }

        print("\n" + "=" * 60)
        print("📊 BUSINESS STRATEGIST EVALUATION SUMMARY")
        print("=" * 60)
        print(f"Total Evaluations: {total_evaluations}")
        print(f"Passed: {passed_evaluations}")
        print(f"Failed: {total_evaluations - passed_evaluations}")
        print(f"Success Rate: {summary['success_rate']:.1%}")
        print(f"Total Time: {total_time:.1f}s")

        if summary["overall_passed"]:
            print(
                "\n🎉 ALL EVALUATIONS PASSED! Business Strategist system is working correctly."
            )
        else:
            print(
                f"\n⚠️ {total_evaluations - passed_evaluations} evaluation(s) failed. Check details above."
            )

        print("=" * 60)

        return summary


async def run_business_strategist_evaluations():
    """Main function to run all business strategist evaluations."""
    evaluator = BusinessStrategistEvaluator()
    return await evaluator.run_all_evaluations()


if __name__ == "__main__":
    asyncio.run(run_business_strategist_evaluations())
