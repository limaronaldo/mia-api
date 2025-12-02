"""
Example demonstrating the partner handoff functionality in the guide_agent decorator.

This example shows how to create agents that can transfer conversations to each other
using the partners parameter in the @guide_agent decorator.
"""

from textwrap import dedent
from typing import List

from langchain_core.messages import BaseMessage
from langchain_core.runnables import Runnable
from langgraph.types import StreamWriter

from src.infrastructure.ai.graphs.chat.state import State
from src.infrastructure.lib.ai.agent_decorator import guide_agent


# Example 1: General Assistant with Multiple Partners
@guide_agent(
    agent_name="GeneralAssistant",
    partners=["research_agent", "technical_agent", "sales_agent"],
    system_prompt=dedent("""
        You are a general assistant that can help with various tasks.
        When you encounter specialized requests, you should transfer the conversation
        to the appropriate specialist agent:

        - For research tasks: use transfer_to_research_agent
        - For technical problems: use transfer_to_technical_agent
        - For sales inquiries: use transfer_to_sales_agent

        Always provide a clear task description when transferring.
    """),
)
async def general_assistant(
    state: State,
    writer: StreamWriter,
    model: Runnable,
) -> dict:
    """General assistant that can handoff to specialist agents."""

    messages: List[BaseMessage] = state.get("messages", [])

    # The model now has access to:
    # - transfer_to_research_agent(task_description: str)
    # - transfer_to_technical_agent(task_description: str)
    # - transfer_to_sales_agent(task_description: str)

    response = await model.ainvoke({"messages": messages})
    return response


# Example 2: Research Specialist (can handoff back to general)
@guide_agent(
    agent_name="research_agent",
    partners=["GeneralAssistant"],
    system_prompt=dedent("""
        You are a research specialist. You excel at finding information,
        analyzing data, and providing detailed research reports.

        If the user asks for something outside your research expertise,
        transfer back to the GeneralAssistant using transfer_to_GeneralAssistant.
    """),
)
async def research_agent(
    state: State,
    writer: StreamWriter,
    model: Runnable,
) -> dict:
    """Research specialist agent."""

    messages: List[BaseMessage] = state.get("messages", [])
    response = await model.ainvoke({"messages": messages})
    return response


# Example 3: Technical Support Agent
@guide_agent(
    agent_name="technical_agent",
    partners=["GeneralAssistant", "research_agent"],
    system_prompt=dedent("""
        You are a technical support specialist. You help with technical problems,
        debugging, and system troubleshooting.

        If you need research assistance, transfer to research_agent.
        For non-technical questions, transfer to GeneralAssistant.
    """),
)
async def technical_agent(
    state: State,
    writer: StreamWriter,
    model: Runnable,
) -> dict:
    """Technical support specialist agent."""

    messages: List[BaseMessage] = state.get("messages", [])
    response = await model.ainvoke({"messages": messages})
    return response


# Example 4: Sales Agent (no partners - terminal agent)
@guide_agent(
    agent_name="sales_agent",
    system_prompt=dedent("""
        You are a sales specialist. You handle all sales inquiries,
        pricing questions, and deal negotiations.

        You are the final destination for sales-related conversations.
    """),
)
async def sales_agent(
    state: State,
    writer: StreamWriter,
    model: Runnable,
) -> dict:
    """Sales specialist agent - terminal node."""

    messages: List[BaseMessage] = state.get("messages", [])
    response = await model.ainvoke({"messages": messages})
    return response


"""
How the partner handoff system works:

1. **Automatic Tool Creation**: When you specify partners=["agent1", "agent2"],
   the decorator automatically creates handoff tools:
   - transfer_to_agent1(task_description: str)
   - transfer_to_agent2(task_description: str)

2. **Task Description**: Each handoff tool requires a task_description parameter
   that explains what the next agent should do, including context.

3. **LangGraph Commands**: The handoff tools return LangGraph Command objects
   that route the conversation to the specified agent.

4. **Bidirectional**: Agents can handoff to each other in any direction,
   creating flexible conversation flows.

Usage Examples:

# User asks general assistant: "I need research on market trends"
# General assistant calls: transfer_to_research_agent("Research current market trends in real estate, focusing on luxury properties")

# User asks technical agent: "What's the best CRM software?"
# Technical agent calls: transfer_to_research_agent("Research and compare top CRM software solutions for real estate businesses")

# Research agent finishes and user asks: "How much does this cost?"
# Research agent calls: transfer_to_sales_agent("User is interested in CRM software pricing after reviewing research on top solutions")

Example of Automatic Partner Instructions:
When the GeneralAssistant is created with partners=["research_agent", "technical_agent", "sales_agent"],
the system automatically appends these instructions to the system prompt:

"<IMPORTANT_PARTNER_GUIDELINES>
You have access to specialized partner agents: research_agent, technical_agent, sales_agent.

CRITICAL: If a user's question or request is related to any of these specialized areas, you MUST transfer the conversation to the appropriate partner agent using the transfer_to_[partner_name] tool.

Available transfers:
- transfer_to_research_agent: Use when the conversation involves research_agent-related topics or specialized assistance
- transfer_to_technical_agent: Use when the conversation involves technical_agent-related topics or specialized assistance
- transfer_to_sales_agent: Use when the conversation involves sales_agent-related topics or specialized assistance

Always provide a comprehensive task_description when transferring, including:
- Complete context of the user's request
- Relevant conversation history
- Specific requirements or preferences mentioned
- Any important details the partner agent needs to know

Do NOT attempt to handle specialized requests yourself when a partner agent is available.
</IMPORTANT_PARTNER_GUIDELINES>"

This ensures agents automatically know to transfer conversations to appropriate specialists!
"""
