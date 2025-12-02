"""
Examples demonstrating Smart Agent Graph Generation

This file shows how to use the enhanced @guide_agent decorator to create:
1. Isolated agent graphs (each agent has its own complete workflow)
2. Multi-agent systems with handoff capabilities
3. Hybrid approaches combining both patterns
"""

from textwrap import dedent
from typing import List

from langchain_core.messages import BaseMessage
from pydantic import BaseModel, Field

from src.infrastructure.ai.graphs.chat.state import State
from src.infrastructure.lib.ai.agent_decorator import (
    create_multi_agent_system,
    guide_agent,
)

# Example 1: Isolated Agent Graph
# Each agent gets its own complete workflow with tools, validation, retry logic


class ResearchResult(BaseModel):
    """Structured output for research agent."""

    summary: str = Field(description="Brief summary of research findings")
    key_points: List[str] = Field(description="List of key findings")
    sources: List[str] = Field(description="List of source references")


# This creates an isolated graph for the research agent
@guide_agent(
    agent_name="research_agent",
    model="standard",
    system_prompt=dedent("""
        You are a research specialist AI. You excel at:
        - Finding and analyzing information
        - Providing structured research reports
        - Citing reliable sources

        Always provide comprehensive research with proper citations.
    """),
    response_model=ResearchResult,
    create_graph=True,  # This creates an isolated graph
    state_class=State,
    description="Research specialist that finds and analyzes information, provides structured reports with citations, and handles complex data analysis tasks",
)
async def research_agent(state: State, writer, model) -> State:
    """Research agent with isolated graph and structured output."""
    messages: List[BaseMessage] = state.get("messages", [])

    # Agent logic here - the decorator handles all the infrastructure
    response = await model.ainvoke({"messages": messages})

    return {"messages": state["messages"] + [response]}


# Example 2: Customer Service Agent with Handoffs
@guide_agent(
    agent_name="customer_service",
    model="standard",
    system_prompt=dedent("""
        You are a customer service representative. You help with:
        - General inquiries and support
        - Account-related questions
        - Routing complex issues to specialists

        Transfer technical issues to technical_support agent.
        Transfer billing issues to billing_specialist agent.
    """),
    partners=["technical_support", "billing_specialist"],
    create_graph=True,
    state_class=State,
    description="Customer service representative handling general inquiries, account questions, and routing complex issues to appropriate specialists",
)
async def customer_service_agent(state: State, writer, model) -> State:
    """Customer service agent that can handoff to specialists."""
    messages: List[BaseMessage] = state.get("messages", [])

    response = await model.ainvoke({"messages": messages})
    return {"messages": state["messages"] + [response]}


# Example 3: Technical Support Specialist
@guide_agent(
    agent_name="technical_support",
    model="heavy",  # More powerful model for complex technical issues
    system_prompt=dedent("""
        You are a technical support specialist. You handle:
        - System troubleshooting
        - Software configuration issues
        - Integration problems

        If you need additional research, transfer to research_agent.
        For billing-related technical issues, transfer to billing_specialist.
    """),
    partners=["research_agent", "billing_specialist", "customer_service"],
    create_graph=True,
    state_class=State,
    description="Technical support specialist handling system troubleshooting, software configuration, integration problems, and complex technical issues",
)
async def technical_support_agent(state: State, writer, model) -> State:
    """Technical support specialist with research capabilities."""
    messages: List[BaseMessage] = state.get("messages", [])

    response = await model.ainvoke({"messages": messages})
    return {"messages": state["messages"] + [response]}


# Example 4: Billing Specialist
@guide_agent(
    agent_name="billing_specialist",
    model="standard",
    system_prompt=dedent("""
        You are a billing specialist. You handle:
        - Payment processing issues
        - Subscription management
        - Invoice inquiries

        For technical billing system issues, transfer to technical_support.
        For general questions, transfer back to customer_service.
    """),
    partners=["technical_support", "customer_service"],
    create_graph=True,
    state_class=State,
    description="Billing specialist managing payment processing, subscription management, invoice inquiries, and financial account issues",
)
async def billing_specialist_agent(state: State, writer, model) -> State:
    """Billing specialist with handoff capabilities."""
    messages: List[BaseMessage] = state.get("messages", [])

    response = await model.ainvoke({"messages": messages})
    return {"messages": state["messages"] + [response]}


# Example 5: Creating Multi-Agent Systems


def create_customer_support_system():
    """
    Create a complete customer support system with multiple specialized agents.
    """

    # All agents are created with create_graph=True, so each has isolated flows
    agents = [
        customer_service_agent,
        technical_support_agent,
        billing_specialist_agent,
        research_agent,
    ]

    # Create multi-agent system with handoff capabilities
    support_system = create_multi_agent_system(
        agents=agents,
        state_class=State,
        # checkpointer=your_checkpointer  # Optional for persistence
    )

    return support_system


def create_real_estate_system():
    """
    Create MBRAS real estate system using the smart graph generation.
    """

    # Import the existing agents (they should be updated to use create_graph=True)
    from src.infrastructure.ai.graphs.chat.agents.general import call_agent
    from src.infrastructure.ai.graphs.chat.agents.lead_seeker import call_lead_seeker

    # Create multi-agent real estate system
    real_estate_system = create_multi_agent_system(
        agents=[call_agent, call_lead_seeker],
        state_class=State,
        # checkpointer=memory  # Use your existing checkpointer
    )

    return real_estate_system


# Example 6: Hybrid Approach - Mix of Isolated and Shared Agents


# This agent works in isolation
@guide_agent(
    agent_name="data_analyzer",
    system_prompt="You analyze data and provide insights.",
    create_graph=True,
    state_class=State,
    description="Data analysis specialist that processes datasets, generates insights, creates visualizations, and provides statistical analysis",
)
async def isolated_analyzer(state: State, writer, model) -> State:
    """Completely isolated data analysis agent."""
    return state


# These agents work together in a shared system
@guide_agent(
    agent_name="coordinator",
    partners=["specialist"],
    system_prompt="You coordinate tasks and delegate to specialists.",
    description="Task coordinator that manages workflow, delegates tasks to specialists, and ensures efficient task completion",
)
async def coordinator_agent(state: State, writer, model) -> State:
    """Coordinator in shared system."""
    return state


@guide_agent(
    agent_name="specialist",
    partners=["coordinator"],
    system_prompt="You handle specialized tasks.",
    description="Specialist agent that handles complex specialized tasks requiring domain expertise and detailed knowledge",
)
async def specialist_agent(state: State, writer, model) -> State:
    """Specialist in shared system."""
    return state


# Usage Examples and Benefits

"""
Benefits of Smart Agent Graph Generation:

1. **Isolated Flows**: Each agent has its own complete workflow
   - Tools execution
   - Response validation
   - Retry logic
   - Error handling

2. **No Code Duplication**: All infrastructure is handled by decorator
   - Automatic graph creation
   - Standard routing logic
   - Event emission
   - State management

3. **Flexible Architecture**: Mix and match approaches
   - Some agents isolated (create_graph=True)
   - Some agents in shared systems
   - Multi-agent systems with handoffs

4. **Easy Scaling**: Add new agents without touching existing code
   - Just create new @guide_agent functions
   - Automatic tool integration
   - Automatic handoff capabilities

5. **Consistent Behavior**: All agents get same infrastructure
   - Response handling
   - Event emission
   - Memory management
   - Retry logic

Usage Examples:

# Run isolated agent
research_graph = research_agent  # This is now a compiled graph
result = await research_graph.ainvoke({"messages": [user_message]})

# Run multi-agent system
support_system = create_customer_support_system()
result = await support_system.ainvoke({"messages": [user_message]})

# Each agent maintains its own state and flow while supporting handoffs
"""


# Example 7: Advanced Configuration


@guide_agent(
    agent_name="advanced_agent",
    model="heavy",
    tools=[],  # Add your custom tools here
    system_prompt="Advanced agent with all features",
    partners=["research_agent", "technical_support"],
    response_model=None,  # Or use a Pydantic model for structured output
    custom_prompt_template=None,  # Or provide custom template
    create_graph=True,
    state_class=State,
    description="Advanced multi-capability agent with full feature set including research, technical support, and comprehensive task handling",
)
async def advanced_agent_example(
    state: State, writer, model, base_model, prompt_template
) -> State:
    """
    Advanced agent showing all available parameters and features.

    Available in function parameters:
    - state: Current state
    - writer: Event writer
    - model: Chained model (prompt + model + tools/structured_output)
    - base_model: Raw model (for advanced operations like with_structured_output)
    - prompt_template: The prompt template being used
    """

    messages = state.get("messages", [])

    # Use the chained model for standard operations
    response = await model.ainvoke({"messages": messages})

    # Or use base_model for advanced operations
    # structured_model = base_model.with_structured_output(SomeModel)
    # custom_chain = prompt_template | structured_model
    # response = await custom_chain.ainvoke({...})

    return {"messages": state["messages"] + [response]}


if __name__ == "__main__":
    print("Smart Agent Graph Examples")
    print("=" * 50)

    print("\n🤖 Individual Agents (Isolated Graphs):")
    print("- research_agent: Complete isolated workflow")
    print("- customer_service: Isolated with handoff capabilities")
    print("- technical_support: Advanced troubleshooting")
    print("- billing_specialist: Payment and subscription handling")

    print("\n🌐 Multi-Agent Systems:")
    print("- Customer Support System: 4 agents with handoffs")
    print("- Real Estate System: Property search + lead generation")

    print("\n⚡ Key Features:")
    print("- Zero code duplication")
    print("- Automatic graph generation")
    print("- Isolated agent workflows")
    print("- Multi-agent handoff systems")
    print("- Flexible architecture options")

    print("\n🚀 Each agent gets automatically:")
    print("- Tools execution flow")
    print("- Response validation")
    print("- Retry logic")
    print("- Event emission")
    print("- Memory management")
    print("- Partner handoff capabilities")
