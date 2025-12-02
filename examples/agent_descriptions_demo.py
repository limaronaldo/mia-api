"""
Agent Descriptions Demo
======================

This file demonstrates the new agent description functionality that provides
better context for partner transfers. When agents have descriptive information,
partner transfers become more intelligent and contextually appropriate.
"""

from textwrap import dedent
from typing import List

from langchain_core.messages import BaseMessage

from src.infrastructure.ai.graphs.chat.state import State
from src.infrastructure.lib.ai.agent_decorator import (
    get_agent_description,
    get_registered_agents,
    guide_agent,
    is_agent_registered,
)


# Example 1: Comprehensive Real Estate System with Descriptions
@guide_agent(
    agent_name="PropertySearch",
    partners=["PropertyListing", "MortgageAdvice", "LegalSupport"],
    system_prompt=dedent("""
        You help customers find properties that match their criteria.
        Use search tools to find properties and provide recommendations.
    """),
    description="Property search specialist that helps customers find homes, apartments, and commercial properties using advanced search filters and market knowledge",
)
async def property_search_agent(state: State, writer, model) -> dict:
    """Property search agent with intelligent partner transfers."""

    messages: List[BaseMessage] = state.get("messages", [])

    # The agent now automatically gets enhanced partner instructions like:
    # - transfer_to_PropertyListing: Property listing specialist that guides property owners through...
    # - transfer_to_MortgageAdvice: Mortgage and financing advisor that helps with loan applications...
    # - transfer_to_LegalSupport: Legal support specialist handling contracts, documentation...

    response = await model.ainvoke({"messages": messages})
    return response


@guide_agent(
    agent_name="PropertyListing",
    partners=["PropertySearch", "MarketAnalysis"],
    system_prompt=dedent("""
        You guide property owners through the listing process.
        Collect property details and explain listing requirements.
    """),
    description="Property listing specialist that guides property owners through the listing process, collects essential property details, explains MBRAS listing requirements, and manages property announcements",
)
async def property_listing_agent(state: State, writer, model) -> dict:
    """Property listing agent."""

    messages: List[BaseMessage] = state.get("messages", [])
    response = await model.ainvoke({"messages": messages})
    return response


@guide_agent(
    agent_name="MortgageAdvice",
    partners=["PropertySearch", "LegalSupport"],
    system_prompt=dedent("""
        You provide mortgage and financing advice.
        Help with loan applications and financial planning.
    """),
    description="Mortgage and financing advisor that helps with loan applications, interest rate analysis, financing options, and financial planning for property purchases",
)
async def mortgage_advice_agent(state: State, writer, model) -> dict:
    """Mortgage advice agent."""

    messages: List[BaseMessage] = state.get("messages", [])
    response = await model.ainvoke({"messages": messages})
    return response


@guide_agent(
    agent_name="LegalSupport",
    partners=["PropertySearch", "PropertyListing"],
    system_prompt=dedent("""
        You handle legal aspects of real estate transactions.
        Assist with contracts, documentation, and legal requirements.
    """),
    description="Legal support specialist handling contracts, documentation, legal requirements, compliance issues, and transaction legal processes for real estate deals",
)
async def legal_support_agent(state: State, writer, model) -> dict:
    """Legal support agent."""

    messages: List[BaseMessage] = state.get("messages", [])
    response = await model.ainvoke({"messages": messages})
    return response


@guide_agent(
    agent_name="MarketAnalysis",
    partners=["PropertySearch", "PropertyListing"],
    system_prompt=dedent("""
        You provide market analysis and property valuation.
        Analyze market trends and property values.
    """),
    description="Market analysis specialist providing property valuations, market trend analysis, comparative market analysis, and investment advice for real estate decisions",
)
async def market_analysis_agent(state: State, writer, model) -> dict:
    """Market analysis agent."""

    messages: List[BaseMessage] = state.get("messages", [])
    response = await model.ainvoke({"messages": messages})
    return response


# Example 2: Customer Support System with Descriptions
@guide_agent(
    agent_name="GeneralSupport",
    partners=["TechnicalSupport", "BillingSupport", "ProductSupport"],
    system_prompt="You handle general customer inquiries and route to specialists.",
    description="General customer support representative handling initial inquiries, account questions, and routing customers to appropriate specialized support teams",
)
async def general_support_agent(state: State, writer, model) -> dict:
    """General support with smart routing to specialists."""
    return await model.ainvoke({"messages": state.get("messages", [])})


@guide_agent(
    agent_name="TechnicalSupport",
    partners=["GeneralSupport", "ProductSupport"],
    system_prompt="You resolve technical issues and system problems.",
    description="Technical support specialist resolving software bugs, system configuration issues, integration problems, and complex technical troubleshooting",
)
async def technical_support_agent(state: State, writer, model) -> dict:
    """Technical support specialist."""
    return await model.ainvoke({"messages": state.get("messages", [])})


@guide_agent(
    agent_name="BillingSupport",
    partners=["GeneralSupport", "TechnicalSupport"],
    system_prompt="You handle billing, payments, and subscription issues.",
    description="Billing support specialist managing payment processing, subscription changes, invoice disputes, refunds, and financial account management",
)
async def billing_support_agent(state: State, writer, model) -> dict:
    """Billing support specialist."""
    return await model.ainvoke({"messages": state.get("messages", [])})


@guide_agent(
    agent_name="ProductSupport",
    partners=["GeneralSupport", "TechnicalSupport"],
    system_prompt="You provide product guidance and feature explanations.",
    description="Product support specialist explaining features, providing usage guidance, training customers, and helping with product optimization and best practices",
)
async def product_support_agent(state: State, writer, model) -> dict:
    """Product support specialist."""
    return await model.ainvoke({"messages": state.get("messages", [])})


# Utility Functions for Demo
def demonstrate_agent_registry():
    """Demonstrate the agent registry functionality."""

    print("=== AGENT REGISTRY DEMONSTRATION ===\n")

    # Show all registered agents
    registered_agents = get_registered_agents()
    print(f"📋 Total registered agents: {len(registered_agents)}\n")

    for agent_name, description in registered_agents.items():
        print(f"🤖 {agent_name}:")
        print(f"   📝 {description}")
        print()

    # Demonstrate agent lookup
    print("=== AGENT LOOKUP EXAMPLES ===\n")

    test_agents = ["PropertySearch", "TechnicalSupport", "NonExistentAgent"]

    for agent in test_agents:
        is_registered = is_agent_registered(agent)
        description = get_agent_description(agent)
        status = "✅ Registered" if is_registered else "❌ Not registered"

        print(f"🔍 {agent}: {status}")
        print(f"   📄 Description: {description}")
        print()


def show_enhanced_partner_instructions():
    """Show how partner instructions are enhanced with descriptions."""

    print("=== ENHANCED PARTNER INSTRUCTIONS ===\n")

    print("🏠 PropertySearch Agent Partner Instructions:")
    print("-" * 50)

    # Simulate what gets added to PropertySearch agent's system prompt
    partners = ["PropertyListing", "MortgageAdvice", "LegalSupport"]

    print("Available transfers:")
    for partner in partners:
        description = get_agent_description(partner)
        print(f"- transfer_to_{partner}: {description}")

    print("\n" + "=" * 70 + "\n")

    print("🎧 GeneralSupport Agent Partner Instructions:")
    print("-" * 50)

    partners = ["TechnicalSupport", "BillingSupport", "ProductSupport"]

    print("Available transfers:")
    for partner in partners:
        description = get_agent_description(partner)
        print(f"- transfer_to_{partner}: {description}")


def demonstrate_conversation_scenarios():
    """Show conversation scenarios with intelligent routing."""

    print("=== CONVERSATION SCENARIOS ===\n")

    scenarios = [
        {
            "user_message": "I'm looking for a 3-bedroom apartment in São Paulo under R$ 800,000",
            "expected_agent": "PropertySearch",
            "reasoning": "Property search request with specific criteria",
        },
        {
            "user_message": "I want to sell my house, what do I need to do?",
            "expected_transfer": "transfer_to_PropertyListing",
            "reasoning": "Property listing inquiry - PropertySearch would transfer to PropertyListing",
        },
        {
            "user_message": "What mortgage rates are available for first-time buyers?",
            "expected_transfer": "transfer_to_MortgageAdvice",
            "reasoning": "Mortgage inquiry - would be transferred to mortgage specialist",
        },
        {
            "user_message": "I need help reviewing the purchase contract",
            "expected_transfer": "transfer_to_LegalSupport",
            "reasoning": "Legal assistance needed - would transfer to legal specialist",
        },
        {
            "user_message": "The app is crashing when I try to save searches",
            "expected_transfer": "transfer_to_TechnicalSupport",
            "reasoning": "Technical issue - GeneralSupport would transfer to technical specialist",
        },
        {
            "user_message": "I was charged twice for my subscription",
            "expected_transfer": "transfer_to_BillingSupport",
            "reasoning": "Billing issue - would be transferred to billing specialist",
        },
    ]

    for i, scenario in enumerate(scenarios, 1):
        print(f"📋 Scenario {i}:")
        print(f'   👤 User: "{scenario["user_message"]}"')

        if "expected_agent" in scenario:
            print(f"   🎯 Handled by: {scenario['expected_agent']}")

        if "expected_transfer" in scenario:
            agent_name = scenario["expected_transfer"].replace("transfer_to_", "")
            description = get_agent_description(agent_name)
            print(f"   🔄 Expected Transfer: {scenario['expected_transfer']}")
            print(f"   📝 Target Agent: {description}")

        print(f"   🧠 Reasoning: {scenario['reasoning']}")
        print()


def compare_before_after():
    """Compare partner instructions before and after descriptions."""

    print("=== BEFORE vs AFTER DESCRIPTIONS ===\n")

    print("🔴 BEFORE (Generic descriptions):")
    print("-" * 40)
    print("Available transfers:")
    print(
        "- transfer_to_PropertyListing: Use when conversation involves PropertyListing-related topics"
    )
    print(
        "- transfer_to_MortgageAdvice: Use when conversation involves MortgageAdvice-related topics"
    )
    print(
        "- transfer_to_LegalSupport: Use when conversation involves LegalSupport-related topics"
    )

    print("\n🟢 AFTER (Descriptive context):")
    print("-" * 40)
    print("Available transfers:")
    partners = ["PropertyListing", "MortgageAdvice", "LegalSupport"]
    for partner in partners:
        description = get_agent_description(partner)
        print(f"- transfer_to_{partner}: {description}")

    print("\n💡 Benefits:")
    print("   ✅ Agents understand exactly when to transfer")
    print("   ✅ More accurate routing decisions")
    print("   ✅ Better user experience with faster resolution")
    print("   ✅ Reduced back-and-forth between agents")
    print("   ✅ Clear specialization boundaries")


if __name__ == "__main__":
    print("🎯 AGENT DESCRIPTIONS SYSTEM DEMONSTRATION")
    print("=" * 60)
    print()

    print("This demo shows how agent descriptions improve partner transfers")
    print("by providing contextual information about each agent's capabilities.")
    print()

    # Run demonstrations
    demonstrate_agent_registry()
    print("\n" + "=" * 70 + "\n")

    show_enhanced_partner_instructions()
    print("\n" + "=" * 70 + "\n")

    demonstrate_conversation_scenarios()
    print("\n" + "=" * 70 + "\n")

    compare_before_after()
    print("\n" + "=" * 70 + "\n")

    print("🎉 SUMMARY:")
    print("The description parameter enables:")
    print("  🎯 Intelligent agent routing")
    print("  🔄 Context-aware transfers")
    print("  📝 Clear agent specializations")
    print("  ⚡ Faster problem resolution")
    print("  🎭 Better user experience")
    print()
    print("Use descriptions to build smarter multi-agent systems! 🚀")


"""
USAGE EXAMPLES:

# Basic usage with description
@guide_agent(
    agent_name="MyAgent",
    description="Specialist that handles X, Y, and Z tasks with expertise in domain A"
)
async def my_agent(state, writer, model):
    return response

# Advanced usage with partners and descriptions
@guide_agent(
    agent_name="Coordinator",
    partners=["specialist1", "specialist2"],
    description="Task coordinator managing workflows and delegating to specialists",
)
async def coordinator(state, writer, model):
    # Automatic partner instructions will include specialist descriptions
    return response

# Registry management
from src.infrastructure.lib.ai.agent_decorator import get_registered_agents

# Check all registered agents
agents = get_registered_agents()
for name, desc in agents.items():
    print(f"{name}: {desc}")
"""
