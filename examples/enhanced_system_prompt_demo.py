"""
Demonstration of Enhanced System Prompt with Automatic Partner Instructions

This file shows how the agent_decorator automatically enhances system prompts
when partners are provided, ensuring agents know to transfer conversations
to appropriate specialists.
"""


# Example of what happens internally when using partners
def demonstrate_enhanced_prompt():
    """Shows the before/after of system prompt enhancement."""

    # Original system prompt (what developer writes)
    original_prompt = """
    <agent>
        <identity>
            <name>General Assistant</name>
            <role>Helpful AI Assistant</role>
            <description>I help users with various tasks and questions.</description>
        </identity>

        <core_capabilities>
        - Answer general questions
        - Provide helpful information
        - Guide users to appropriate resources
        </core_capabilities>

        <communication_guidelines>
        - Be helpful and polite
        - Keep responses concise
        - Ask clarifying questions when needed
        </communication_guidelines>
    </agent>
    """

    # Partners list provided to decorator
    partners = ["research_agent", "technical_support", "sales_specialist"]

    # What the decorator automatically appends
    partner_instructions = """

        <IMPORTANT_PARTNER_GUIDELINES>
        You have access to specialized partner agents: research_agent, technical_support, sales_specialist.

        CRITICAL: If a user's question or request is related to any of these specialized areas, you MUST transfer the conversation to the appropriate partner agent using the transfer_to_[partner_name] tool.

        Available transfers:
        - transfer_to_research_agent: Use when the conversation involves research_agent-related topics or specialized assistance
        - transfer_to_technical_support: Use when the conversation involves technical_support-related topics or specialized assistance
        - transfer_to_sales_specialist: Use when the conversation involves sales_specialist-related topics or specialized assistance

        Always provide a comprehensive task_description when transferring, including:
        - Complete context of the user's request
        - Relevant conversation history
        - Specific requirements or preferences mentioned
        - Any important details the partner agent needs to know

        Do NOT attempt to handle specialized requests yourself when a partner agent is available.
        </IMPORTANT_PARTNER_GUIDELINES>"""

    # Final enhanced system prompt (what the model actually receives)
    enhanced_prompt = original_prompt + partner_instructions

    return {
        "original": original_prompt,
        "partners": partners,
        "partner_instructions": partner_instructions,
        "enhanced": enhanced_prompt,
    }


# Real-world example with MBRAS agents
def mbras_example():
    """Shows how MBRAS general agent gets enhanced with lead_seeker partner."""

    # What developer writes (example - not actual import)
    # @guide_agent(
    #     agent_name="Broker",
    #     tools=chat_tools,
    #     system_prompt="You are a luxury real estate assistant...",
    #     partners=["lead_seeker"],  # This triggers automatic enhancement
    # )
    # async def call_agent(state, writer, model):
    #     # Agent now automatically knows:
    #     # "If user wants to list property, transfer to lead_seeker"
    #     # "Use transfer_to_lead_seeker tool with comprehensive task_description"
    #     pass

    # System automatically appends:
    automatic_instructions = """
        <IMPORTANT_PARTNER_GUIDELINES>
        You have access to specialized partner agents: lead_seeker.

        CRITICAL: If a user's question or request is related to any of these specialized areas, you MUST transfer the conversation to the appropriate partner agent using the transfer_to_[partner_name] tool.

        Available transfers:
        - transfer_to_lead_seeker: Use when the conversation involves lead_seeker-related topics or specialized assistance

        Always provide a comprehensive task_description when transferring, including:
        - Complete context of the user's request
        - Relevant conversation history
        - Specific requirements or preferences mentioned
        - Any important details the partner agent needs to know

        Do NOT attempt to handle specialized requests yourself when a partner agent is available.
        </IMPORTANT_PARTNER_GUIDELINES>"""

    return automatic_instructions


# Conversation flow examples
def conversation_examples():
    """Shows how enhanced prompts lead to automatic transfers."""

    examples = [
        {
            "user_message": "I want to list my apartment for sale",
            "agent_behavior": "Automatically transfers to lead_seeker",
            "transfer_call": "transfer_to_lead_seeker('User wants to list their apartment for sale. Need to collect property details, location, pricing, and owner contact information for MBRAS listing process.')",
            "reasoning": "Listing property = lead_seeker specialty, automatic transfer",
        },
        {
            "user_message": "What's the market research on São Paulo luxury condos?",
            "agent_behavior": "Automatically transfers to research_agent (if available)",
            "transfer_call": "transfer_to_research_agent('User needs market research on luxury condominium properties in São Paulo. Should include price trends, market analysis, and comparable properties.')",
            "reasoning": "Market research = research_agent specialty, automatic transfer",
        },
        {
            "user_message": "I'm having trouble with the property search feature",
            "agent_behavior": "Automatically transfers to technical_support (if available)",
            "transfer_call": "transfer_to_technical_support('User experiencing issues with property search functionality. Need technical assistance to troubleshoot and resolve the problem.')",
            "reasoning": "Technical problem = technical_support specialty, automatic transfer",
        },
    ]

    return examples


# Benefits of automatic partner instructions
def benefits():
    """Lists benefits of automatic partner instructions."""

    return {
        "consistency": "All agents with partners automatically know to transfer appropriately",
        "no_manual_instructions": "Developers don't need to manually write transfer instructions",
        "comprehensive_context": "Automatic instructions ensure proper task_description usage",
        "prevents_scope_creep": "Agents don't try to handle tasks outside their expertise",
        "scalability": "Easy to add new partners without updating system prompts",
        "maintainability": "Partner behavior is centralized in the decorator",
        "flexibility": "Works with any partner combination automatically",
    }


if __name__ == "__main__":
    # Demo the enhancement process
    demo = demonstrate_enhanced_prompt()
    print("=== ORIGINAL SYSTEM PROMPT ===")
    print(demo["original"])

    print("\n=== PARTNERS PROVIDED ===")
    print(demo["partners"])

    print("\n=== AUTOMATIC ENHANCEMENT ===")
    print(demo["partner_instructions"])

    print("\n=== FINAL ENHANCED PROMPT ===")
    print(demo["enhanced"])

    print("\n=== CONVERSATION EXAMPLES ===")
    examples = conversation_examples()
    for i, example in enumerate(examples, 1):
        print(f"\nExample {i}:")
        print(f"User: {example['user_message']}")
        print(f"Agent: {example['agent_behavior']}")
        print(f"Tool Call: {example['transfer_call']}")
        print(f"Why: {example['reasoning']}")

    print("\n=== BENEFITS ===")
    benefits_list = benefits()
    for benefit, description in benefits_list.items():
        print(f"• {benefit.title()}: {description}")
