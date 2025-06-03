"""
Business Strategy Tools

Tools for interacting with the Business Strategist agent and its sub-agents.
These tools follow the context-passing approach where the root agent curates
relevant context and passes it to the Business Strategist. ADK automatically
handles delegation to specialized sub-agents based on the query type.
"""

import logging

logger = logging.getLogger(__name__)


async def get_business_strategy_advice(
    business_question: str,
    business_context: str = "",
    user_style: str = "",
    tool_context=None,
) -> str:
    """
    Get business strategy advice from the Business Strategist agent.

    The root agent should curate relevant context from memory and user profile.

    Args:
        business_question: The specific business question or challenge
        business_context: Relevant business context, background, and current situation
        user_style: User's decision-making style and preferences
        tool_context: ADK ToolContext (not used by sub-agent but available)

    Returns:
        Business strategy advice and recommendations
    """
    try:
        # Create comprehensive context for the Business Strategist
        formatted_context = f"""Business Strategy Consultation Request:

Question/Challenge: {business_question}

Business Context: {business_context if business_context else "No specific business context provided"}

User Style/Preferences: {user_style if user_style else "No specific style preferences provided"}

Instructions:
1. Analyze the business situation thoroughly
2. Provide comprehensive, actionable business strategy advice
3. Consider the user's style and preferences in your recommendations
4. Break down complex strategies into clear, implementable steps"""

        # Return formatted context for the root agent to pass to Business Strategist
        return f"🎯 **Business Strategy Request:**\n\n{formatted_context}"

    except Exception as e:
        logger.error(f"Business strategy consultation preparation failed: {e}")
        return f"❌ Business strategy consultation temporarily unavailable: {str(e)}"


async def analyze_business_opportunity(
    opportunity_description: str,
    business_context: str = "",
    user_style: str = "",
    tool_context=None,
) -> str:
    """
    Analyze a specific business opportunity using the Business Strategist.

    Args:
        opportunity_description: Description of the business opportunity
        business_context: Current business context and relevant background
        user_style: User's decision-making style and risk tolerance
        tool_context: ADK ToolContext (not used by sub-agent but available)

    Returns:
        Opportunity analysis and strategic recommendations
    """
    try:
        formatted_context = f"""Business Opportunity Analysis Request:

Opportunity: {opportunity_description}

Current Business Context: {business_context if business_context else "No specific business context provided"}

User Style/Preferences: {user_style if user_style else "No specific style preferences provided"}

Instructions:
1. Assess the opportunity thoroughly (market potential, risks, requirements)
2. Consider how it fits with the current business context
3. Evaluate resource requirements and implementation challenges
4. Provide strategic recommendations for pursuing or passing on this opportunity
5. Consider the user's style and risk tolerance in your assessment"""

        return f"📊 **Business Opportunity Analysis Request:**\n\n{formatted_context}"

    except Exception as e:
        logger.error(f"Business opportunity analysis preparation failed: {e}")
        return f"❌ Business opportunity analysis temporarily unavailable: {str(e)}"


async def get_business_strategic_plan(
    business_goal: str,
    business_context: str = "",
    user_style: str = "",
    timeframe: str = "6-12 months",
    tool_context=None,
) -> str:
    """
    Create a strategic business plan for achieving specific goals.

    Args:
        business_goal: The specific business goal to achieve
        business_context: Current business situation and relevant background
        user_style: User's decision-making style and preferences
        timeframe: Timeframe for achieving the goal
        tool_context: ADK ToolContext (not used by sub-agent but available)

    Returns:
        Comprehensive strategic business plan
    """
    try:
        formatted_context = f"""Strategic Business Planning Request:

Business Goal: {business_goal}

Current Business Context: {business_context if business_context else "No specific business context provided"}

User Style/Preferences: {user_style if user_style else "No specific style preferences provided"}

Timeframe: {timeframe}

Instructions:
1. Break down the goal into strategic phases and milestones
2. Identify key resources, capabilities, and partnerships needed
3. Create actionable steps with priorities and timelines
4. Identify potential risks and mitigation strategies
5. Suggest key metrics to track progress
6. Consider the user's style and preferences in planning approach"""

        return f"📋 **Strategic Business Planning Request:**\n\n{formatted_context}"

    except Exception as e:
        logger.error(f"Strategic business planning preparation failed: {e}")
        return f"❌ Strategic business planning temporarily unavailable: {str(e)}"


async def get_competitive_analysis(
    competitor_info: str,
    business_context: str = "",
    user_style: str = "",
    tool_context=None,
) -> str:
    """
    Perform competitive analysis and strategic positioning recommendations.

    Args:
        competitor_info: Information about competitors and competitive landscape
        business_context: Current business context and positioning
        user_style: User's decision-making style and preferences
        tool_context: ADK ToolContext (not used by sub-agent but available)

    Returns:
        Competitive analysis and strategic positioning recommendations
    """
    try:
        formatted_context = f"""Competitive Analysis Request:

Competitive Landscape: {competitor_info}

Current Business Context: {business_context if business_context else "No specific business context provided"}

User Style/Preferences: {user_style if user_style else "No specific style preferences provided"}

Instructions:
1. Analyze the competitive landscape and positioning
2. Identify competitive advantages and disadvantages
3. Recommend strategic positioning and differentiation strategies
4. Suggest tactics for competing effectively
5. Consider market gaps and opportunities
6. Adapt recommendations to the user's style and risk tolerance"""

        return f"⚔️ **Competitive Analysis Request:**\n\n{formatted_context}"

    except Exception as e:
        logger.error(f"Competitive analysis preparation failed: {e}")
        return f"❌ Competitive analysis temporarily unavailable: {str(e)}"


# Function to actually invoke the Business Strategist (for root agent use)
async def invoke_business_strategist(context: str, tool_context=None) -> str:
    """
    Actually invoke the Business Strategist with formatted context.
    This should be called by the root agent after curating context.

    Args:
        context: Formatted context string for the Business Strategist
        tool_context: ADK ToolContext

    Returns:
        Business strategy response
    """
    try:
        # Import here to avoid circular imports
        from ..sub_agents.business_strategist_agent import business_strategist

        # This function would be used by the root agent through AgentTool
        # The actual invocation happens through ADK's agent system
        return f"Business Strategist should be invoked through AgentTool with context:\n{context}"

    except Exception as e:
        logger.error(f"Business strategist invocation failed: {e}")
        return f"❌ Business strategist temporarily unavailable: {str(e)}"
