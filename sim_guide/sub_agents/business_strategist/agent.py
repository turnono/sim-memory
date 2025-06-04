"""
Business Strategist Agent

A specialized agent with MBA-level business expertise that maintains the user's personality
and decision-making style while providing comprehensive business strategy guidance.

Features hierarchical sub-agents for specialized domains:
- Marketing Strategy
- Financial Strategy  
- Operations Strategy
- Product Strategy
- Growth Strategy
"""

import logging
from google.adk import Agent
from google.adk.tools import FunctionTool

# Import prompts
from .prompt import (
    DESCRIPTION,
    INSTRUCTION,
    MARKETING_STRATEGIST_INSTRUCTION,
    FINANCE_STRATEGIST_INSTRUCTION,
    OPERATIONS_STRATEGIST_INSTRUCTION,
    PRODUCT_STRATEGIST_INSTRUCTION,
    GROWTH_STRATEGIST_INSTRUCTION,
)

# Import tools
from .tools import (
    get_business_strategy_advice,
    analyze_business_opportunity,
    get_business_strategic_plan,
    get_competitive_analysis,
    invoke_business_strategist,
)

logger = logging.getLogger(__name__)


# Marketing Strategist Sub-Agent
marketing_strategist = Agent(
    name="marketing_strategist",
    model="gemini-2.0-flash",
    description="Specialized marketing strategy expert for brand positioning, digital marketing, customer acquisition, and campaign optimization. Use for marketing questions.",
    instruction=MARKETING_STRATEGIST_INSTRUCTION,
)

# Finance Strategist Sub-Agent
finance_strategist = Agent(
    name="finance_strategist",
    model="gemini-2.0-flash",
    description="Specialized financial strategy expert for financial planning, funding strategies, cost optimization, and investment decisions. Use for financial questions.",
    instruction=FINANCE_STRATEGIST_INSTRUCTION,
)

# Operations Strategist Sub-Agent
operations_strategist = Agent(
    name="operations_strategist",
    model="gemini-2.0-flash",
    description="Specialized operations strategy expert for process optimization, systems implementation, scaling operations, and performance metrics. Use for operational questions.",
    instruction=OPERATIONS_STRATEGIST_INSTRUCTION,
)

# Product Strategist Sub-Agent
product_strategist = Agent(
    name="product_strategist",
    model="gemini-2.0-flash",
    description="Specialized product strategy expert for product-market fit, user experience, roadmap planning, and product analytics. Use for product development questions.",
    instruction=PRODUCT_STRATEGIST_INSTRUCTION,
)

# Growth Strategist Sub-Agent
growth_strategist = Agent(
    name="growth_strategist",
    model="gemini-2.0-flash",
    description="Specialized growth strategy expert for customer acquisition, growth hacking, viral mechanisms, and scaling strategies. Use for growth and expansion questions.",
    instruction=GROWTH_STRATEGIST_INSTRUCTION,
)

# Business strategy tools
business_strategy_tools = [
    FunctionTool(func=get_business_strategy_advice),
    FunctionTool(func=analyze_business_opportunity),
    FunctionTool(func=get_business_strategic_plan),
    FunctionTool(func=get_competitive_analysis),
    FunctionTool(func=invoke_business_strategist),
]

# Main Business Strategist Agent with Sub-Agents and Tools
business_strategist = Agent(
    name="business_strategist",
    model="gemini-2.0-flash",
    description=DESCRIPTION,
    instruction=INSTRUCTION,
    sub_agents=[
        marketing_strategist,
        finance_strategist,
        operations_strategist,
        product_strategist,
        growth_strategist,
    ],
    tools=business_strategy_tools,
)


def get_business_strategist():
    """
    Returns the business strategist agent for use by the root agent.

    Returns:
        Agent: The configured business strategist with sub-agent capabilities
    """
    return business_strategist


# Export for use in main agent
__all__ = [
    "business_strategist",
    "get_business_strategist",
    "marketing_strategist",
    "finance_strategist",
    "operations_strategist",
    "product_strategist",
    "growth_strategist",
] 