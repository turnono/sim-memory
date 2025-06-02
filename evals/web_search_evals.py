#!/usr/bin/env python3
"""
Web Search Agent Evaluation

Tests the web search agent integration and functionality within the ADK framework.
Validates that the agent can properly use Google's built-in search tool.
"""

import asyncio
import sys
import os
import logging

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sim_guide.sub_agents.web_search_agent import web_search_agent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_web_search_agent_integration():
    """Test that the web search agent is properly configured"""
    print("\n🔍 Testing Web Search Agent Integration")
    print("-" * 50)
    
    try:
        # Check agent configuration
        assert web_search_agent.name == "web_search_specialist"
        assert web_search_agent.model == "gemini-2.0-flash"
        assert len(web_search_agent.tools) == 1
        
        # Check that it has the google_search tool
        tool_names = [str(tool) for tool in web_search_agent.tools]
        has_google_search = any("google_search" in tool_name.lower() for tool_name in tool_names)
        
        if has_google_search:
            print("✅ Web search agent properly configured with google_search tool")
            return True
        else:
            print(f"❌ Web search agent missing google_search tool. Found: {tool_names}")
            return False
        
    except Exception as e:
        print(f"❌ Web search agent integration test failed: {e}")
        return False


async def test_main_agent_integration():
    """Test that the web search agent is properly integrated with the main agent"""
    print("\n🔗 Testing Main Agent Integration")
    print("-" * 50)
    
    try:
        from sim_guide.agent import root_agent
        
        # Check that web search agent is included in tools
        agent_tools = [tool.agent.name for tool in root_agent.tools if hasattr(tool, 'agent')]
        
        if "web_search_specialist" in agent_tools:
            print("✅ Web search agent properly integrated with main agent")
            print(f"Available agent tools: {agent_tools}")
            return True
        else:
            print(f"❌ Web search agent not found in main agent tools: {agent_tools}")
            return False
        
    except Exception as e:
        print(f"❌ Main agent integration test failed: {e}")
        return False


async def test_adk_compliance():
    """Test that the web search agent follows ADK best practices"""
    print("\n📋 Testing ADK Compliance")
    print("-" * 50)
    
    try:
        # Check model requirement (Gemini 2.0 for built-in tools)
        assert "gemini-2.0" in web_search_agent.model, f"Expected Gemini 2.0 model, got: {web_search_agent.model}"
        
        # Check single tool limitation (only one built-in tool per agent)
        assert len(web_search_agent.tools) == 1, f"Expected 1 tool, got: {len(web_search_agent.tools)}"
        
        # Check agent has proper description for delegation
        assert web_search_agent.description, "Agent should have description for proper delegation"
        assert "search" in web_search_agent.description.lower(), "Description should mention search capability"
        
        print("✅ Web search agent follows ADK compliance requirements")
        print(f"  - Model: {web_search_agent.model} (Gemini 2.0 ✓)")
        print(f"  - Tools: {len(web_search_agent.tools)} (Single tool ✓)")
        print(f"  - Description: Present and relevant ✓")
        return True
        
    except AssertionError as e:
        print(f"❌ ADK compliance test failed: {e}")
        return False
    except Exception as e:
        print(f"❌ ADK compliance test error: {e}")
        return False


async def run_all_web_search_tests():
    """Run all web search agent tests"""
    print("🚀 WEB SEARCH AGENT EVALUATION")
    print("=" * 60)
    
    tests = [
        test_web_search_agent_integration,
        test_main_agent_integration,
        test_adk_compliance,
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            logger.error(f"Test {test.__name__} failed with exception: {e}")
            results.append(False)
    
    # Summary
    passed = sum(results)
    total = len(results)
    
    print(f"\n📊 EVALUATION SUMMARY")
    print("=" * 60)
    print(f"Tests passed: {passed}/{total}")
    print(f"Success rate: {passed/total*100:.1f}%")
    
    if passed == total:
        print("✅ Web search agent is properly configured and integrated!")
        print("\n🔧 Usage Notes:")
        print("- Use web_search_specialist for current information")
        print("- Automatically available through main agent delegation")
        print("- Follows ADK best practices for built-in tools")
        return 0
    else:
        print("❌ Some web search agent tests need attention")
        return 1


async def main():
    """Main evaluation function"""
    try:
        exit_code = await run_all_web_search_tests()
        return exit_code
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code) 