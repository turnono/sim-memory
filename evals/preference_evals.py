"""
User Preference System Evaluations

Tests the preference management functionality including:
- Preference detection from user messages
- Preference storage and retrieval
- Tool integration with preferences
- Personalization context generation
- Automatic preference updates
"""

import asyncio
import logging
import time
import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import from the new refactored structure
from sim_guide.sub_agents.memory_manager.services import (
    UserPreferences,
    LifeExperienceLevel,
    CommunicationStyle,
    LifeArea,
    get_user_preferences,
    update_user_preferences,
    analyze_user_message_for_preferences,
    format_preferences_summary,
    get_personalized_instruction_context,
)

from sim_guide.sub_agents.memory_manager.services.user_service import (
    UserPreferenceDetector,
)

# Import tools
from sim_guide.sub_agents.memory_manager.tools.preferences import (
    get_user_preferences,
    set_user_preference,
    analyze_message_for_preferences,
    get_personalization_context,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_preference_detection():
    """Test automatic preference detection from user messages"""

    print("🔍 Testing Preference Detection from Messages")

    try:
        detector = UserPreferenceDetector()
        session_state = {}

        # Test messages with different preference indicators
        test_messages = [
            {
                "message": "Hi, my name is Alice and I'm young and just starting my career",
                "expected_changes": ["name", "life_experience_level", "life_area"],
            },
            {
                "message": "I prefer step by step guidance when dealing with relationships and need motivation",
                "expected_changes": ["communication_style", "life_area"],
            },
            {
                "message": "I'm experienced in management and need practical advice for financial planning",
                "expected_changes": ["life_experience_level", "life_area"],
            },
            {
                "message": "Please give me brief advice, I use a journal and calendar for personal growth",
                "expected_changes": ["communication_style", "tool", "life_area"],
            },
        ]

        total_detections = 0
        successful_detections = 0

        for i, test_case in enumerate(test_messages):
            print(f"\n  📝 Test case {i + 1}: {test_case['message'][:50]}...")

            original_prefs = get_user_preferences(session_state)
            updated_prefs = analyze_user_message_for_preferences(
                test_case["message"], session_state
            )

            # Check for expected changes
            changes_detected = []

            if updated_prefs.user_name != original_prefs.user_name:
                changes_detected.append("name")

            if (
                updated_prefs.life_experience_level
                != original_prefs.life_experience_level
            ):
                changes_detected.append("life_experience_level")

            if updated_prefs.communication_style != original_prefs.communication_style:
                changes_detected.append("communication_style")

            if len(updated_prefs.focus_life_areas) > len(
                original_prefs.focus_life_areas
            ):
                changes_detected.append("life_area")

            if len(updated_prefs.preferred_tools) > len(original_prefs.preferred_tools):
                changes_detected.append("tool")

            # Check if at least one expected change was detected
            expected_met = any(
                change in changes_detected for change in test_case["expected_changes"]
            )

            total_detections += 1
            if expected_met:
                successful_detections += 1
                print(f"    ✅ Detected changes: {changes_detected}")
            else:
                print(
                    f"    ❌ Expected: {test_case['expected_changes']}, Got: {changes_detected}"
                )

        success_rate = (
            successful_detections / total_detections if total_detections > 0 else 0
        )

        return {
            "test_name": "preference_detection",
            "passed": success_rate >= 0.75,  # At least 75% detection success rate
            "metrics": {
                "successful_detections": successful_detections,
                "total_detections": total_detections,
                "success_rate": success_rate,
                "final_preferences": updated_prefs.to_dict(),
            },
        }

    except Exception as e:
        logger.error(f"Error in preference detection test: {e}")
        return {"test_name": "preference_detection", "passed": False, "error": str(e)}


async def test_preference_tools():
    """Test preference management tools"""

    print("🔧 Testing Preference Management Tools")

    try:
        # Create a mock ToolContext for testing
        class MockToolContext:
            def __init__(self):
                self.state = {}

        mock_context = MockToolContext()

        # Test getting initial (empty) preferences
        initial_result = get_user_preferences(mock_context)
        initial_success = isinstance(
            initial_result, str
        ) and not initial_result.startswith("Error:")
        print(f"  📋 Initial preferences result: {initial_success}")

        # Test setting user name
        set_name_result = set_user_preference(
            preference_name="name",
            preference_value="TestUser",
            tool_context=mock_context,
        )
        name_success = (
            isinstance(set_name_result, str)
            and "Successfully updated" in set_name_result
        )
        print(f"  👤 Set name result: {name_success}")

        # Test setting life experience level
        set_exp_result = set_user_preference(
            preference_name="life_experience_level",
            preference_value="experienced",
            tool_context=mock_context,
        )
        exp_success = (
            isinstance(set_exp_result, str) and "Successfully updated" in set_exp_result
        )
        print(f"  🎓 Set life experience level result: {exp_success}")

        # Get final preferences to verify
        final_result = get_user_preferences(mock_context)
        final_success = isinstance(final_result, str) and not final_result.startswith(
            "Error:"
        )

        tool_tests = [initial_success, name_success, exp_success, final_success]

        passed_tools = sum(tool_tests)

        print(f"  ✅ Tool operations passed: {passed_tools}/{len(tool_tests)}")

        return {
            "test_name": "preference_tools",
            "passed": passed_tools == len(tool_tests),
            "metrics": {
                "tool_operations_passed": passed_tools,
                "total_tool_operations": len(tool_tests),
            },
        }

    except Exception as e:
        logger.error(f"Error in preference tools test: {e}")
        return {"test_name": "preference_tools", "passed": False, "error": str(e)}


async def test_personalization_context():
    """Test personalization context generation"""

    print("🎨 Testing Personalization Context Generation")

    try:
        # Test different user profiles
        test_profiles = [
            {
                "name": "Young User",
                "prefs": UserPreferences(
                    user_name="Alice",
                    life_experience_level=LifeExperienceLevel.YOUNG,
                    communication_style=CommunicationStyle.STEP_BY_STEP,
                ),
                "expected_keywords": ["young", "step"],
            },
            {
                "name": "Experienced User",
                "prefs": UserPreferences(
                    user_name="Dr. Smith",
                    life_experience_level=LifeExperienceLevel.EXPERIENCED,
                    communication_style=CommunicationStyle.PRACTICAL,
                ),
                "expected_keywords": ["experienced", "practical"],
            },
        ]

        successful_contexts = 0

        for profile in test_profiles:
            print(f"\n  👤 Testing {profile['name']}...")

            context = get_personalized_instruction_context(profile["prefs"])

            if context:
                print(f"    📝 Generated context: {context[:100]}...")

                # Check if expected keywords are present
                context_lower = context.lower()
                keywords_found = sum(
                    1
                    for keyword in profile["expected_keywords"]
                    if keyword.lower() in context_lower
                )

                if keywords_found > 0:
                    successful_contexts += 1
                    print(f"    ✅ Found expected keywords")
                else:
                    print(f"    ❌ No expected keywords found")
            else:
                print(f"    ⚠️  No context generated")

        return {
            "test_name": "personalization_context",
            "passed": successful_contexts >= len(test_profiles) * 0.5,
            "metrics": {
                "successful_contexts": successful_contexts,
                "total_profiles": len(test_profiles),
            },
        }

    except Exception as e:
        logger.error(f"Error in personalization context test: {e}")
        return {
            "test_name": "personalization_context",
            "passed": False,
            "error": str(e),
        }


async def run_preference_evaluations():
    """Run all preference system evaluations"""

    print("🎯 Starting User Preference System Evaluations")
    print("=" * 60)

    start_time = time.time()

    # Run all tests
    tests = [
        test_preference_detection(),
        test_preference_tools(),
        test_personalization_context(),
    ]

    results = []
    for test in tests:
        result = await test
        results.append(result)
        print()

    # Calculate summary
    total_tests = len(results)
    passed_tests = sum(1 for result in results if result["passed"])

    total_time = time.time() - start_time

    print("=" * 60)
    print(f"🎯 Preference System Evaluation Summary")
    print(
        f"Tests Passed: {passed_tests}/{total_tests} ({passed_tests / total_tests * 100:.1f}%)"
    )
    print(f"Total Time: {total_time:.2f} seconds")
    print()

    # Detail results
    for result in results:
        status = "✅ PASS" if result["passed"] else "❌ FAIL"
        print(f"{status} {result['test_name']}")
        if "metrics" in result:
            for key, value in result["metrics"].items():
                print(f"    {key}: {value}")
        if "error" in result:
            print(f"    Error: {result['error']}")

    return {
        "summary": {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "success_rate": passed_tests / total_tests,
            "total_time": total_time,
        },
        "results": results,
    }


if __name__ == "__main__":
    asyncio.run(run_preference_evaluations())
