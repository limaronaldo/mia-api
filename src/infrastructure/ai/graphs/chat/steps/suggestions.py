from textwrap import dedent
from typing import Any, Dict, List, Optional, Sequence

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph.state import RunnableConfig
from pydantic import BaseModel, Field, field_validator

from src.infrastructure.ai.utils import log_token_consumption
from src.infrastructure.lib.ai.agent_decorator import guide_agent
from src.infrastructure.lib.logger import guide_logger

from ..state import State


class SuggestedQuestions(BaseModel):
    """Model to store AI-generated suggested questions."""

    suggestions: List[str] = Field(
        ..., description="List containing exactly 3 suggested questions."
    )

    @field_validator("suggestions")
    def check_list_length(cls, v):
        if len(v) != 3:
            raise ValueError("The list must contain exactly 3 suggestions.")
        return v


SUGGESTIONS_SYSTEM_PROMPT = dedent(
    """
    <agent>
        <identity>
            <name>MBRAS Guide</name>
            <role>Luxury Real Estate Assistant</role>
            <description>Assist users in finding and providing property information.</description>
        </identity>

        <core_capabilities>
            - Generate relevant follow-up questions based on conversation history.
            - Utilize property data fields to formulate questions.
            - Ensure questions are clear, concise, and relevant.
            - Generate follow-up questions as if you are the user, using first person ("eu", "meu", "minha", etc.).
        </core_capabilities>

        <forbidden_actions>
            - Generate more than 3 questions.
            - Include questions not related to the property data fields.
            - Use any language other than Brazilian Portuguese.
            - Include unnecessary details or context in questions.
            - Write questions in third person or as the assistant.
        </forbidden_actions>

        <critical_instructions>
            - Focus on generating questions that can be answered with the available property data.
            - Ensure all questions are in Brazilian Portuguese.
            - Write all questions in first person, as if you are the user asking.
            - Do not include any system instructions or internal notes in the output.
            - All questions should be relevant to the user's inquiry and the property data provided.
            - Do not include any disclaimers or unnecessary information in the output.
        </critical_instructions>

        <system_knowledge>
            - Full access to MBRAS property database.
            - Advanced property search tools available.
            - Property format: MBXXXXX (3-5 digits after MB).
        </system_knowledge>

        <communication_guidelines>
            <guideline>Use clear and concise language.</guideline>
            <guideline>Match the user's language for communication.</guideline>
            <guideline>Keep responses focused on the user's inquiry.</guideline>
        </communication_guidelines>

        <examples>
            - Quantas suítes possui o MB16311?
            - Opções similares nos Jardins.
            - Me explique um pouco mais sobre as comodidades do terceiro imóvel.
        </examples>

        <property_fields>
            <basic_info>
                <field>property type</field>
                <field>business type</field>
                <field>address</field>
                <field>city</field>
                <field>state</field>
                <field>neighborhood</field>
            </basic_info>
            <values>
                <field>sale value</field>
                <field>rent value</field>
                <field>condo fee</field>
                <field>IPTU</field>
            </values>
            <features>
                <field>bedrooms</field>
                <field>suites</field>
                <field>parking spaces</field>
                <field>total area</field>
                <field>usable area</field>
            </features>
            <amenities>
                <field>unit details</field>
                <field>condo details/features</field>
            </amenities>
            <photos>
                <field>photo quantity</field>
                <field>URLs</field>
            </photos>
            <development>
                <field>name</field>
                <field>building name</field>
            </development>
            <additional>
                <field>title</field>
                <field>description</field>
                <field>promotion text</field>
            </additional>
        </property_fields>

        <conversation_history>
            {messages_history}
        </conversation_history>

        <user_memory>
            {user_memory}
        </user_memory>
    </agent>
    """
)

CUSTOM_SUGGESTIONS_TEMPLATE = ChatPromptTemplate.from_messages(
    [
        ("system", SUGGESTIONS_SYSTEM_PROMPT),
        ("human", "Give me the suggestions."),
    ]
)


def _format_messages_for_prompt(messages: Sequence[BaseMessage]) -> str:
    """Formats message history to include in suggestions prompt."""
    formatted_history = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            formatted_history.append(f"User: {msg.content}")
        elif isinstance(msg, AIMessage):
            content = f"Assistant: {msg.content}"
            if msg.tool_calls:
                for tool_call in msg.tool_calls:
                    tool_name = tool_call.get("name", "")
                    tool_args = tool_call.get("args", {})
                    tool_response = tool_call.get("response", "")
                    content += f"\nTool used: {tool_name}"
                    content += f"\nParameters: {tool_args}"
                    content += f"\nTool response: {tool_response}"
            formatted_history.append(content)
    return "\n".join(formatted_history)


@guide_agent(
    agent_name="suggestion_agent",
    model="lite",
    custom_prompt_template=CUSTOM_SUGGESTIONS_TEMPLATE,
    response_model=SuggestedQuestions,
    spectator_mode=True,
    description="Generates contextual follow-up questions based on conversation history to guide user interactions",
)
async def generate_suggestions_step(
    state: State, config: RunnableConfig, writer, model
) -> State:
    """Generates suggested questions using with_structured_output."""

    system_configs = config.get("configurable").get("system_configs")

    if not system_configs.get("enable_suggestions", False):
        guide_logger.debug("🔥 [suggestion_agent] Suggestions disabled")
        return state

    guide_logger.debug(
        "🔥 [suggestion_agent] Starting suggestion generation (spectator mode)"
    )
    state["suggested_questions"] = None
    loaded_memories: Optional[Dict[str, Any]] = state.get("loaded_memories")

    try:
        MAX_SUGGESTION_HISTORY = 30
        recent_messages = state["messages"][-MAX_SUGGESTION_HISTORY:]
        messages_history_str = _format_messages_for_prompt(recent_messages)

        user_memory_str = "No relevant past interactions found for this conversation."
        if loaded_memories:
            memory_parts = []
            for schema_name, content in loaded_memories.items():
                memory_parts.append(f"### {schema_name} Memory\n{content}")
            user_memory_str = "\n\n".join(memory_parts)

        structured_response: SuggestedQuestions = await model.ainvoke(
            {
                "messages_history": messages_history_str,
                "user_memory": user_memory_str,
            }
        )

        # Log token consumption
        log_token_consumption(
            "suggestion_agent", structured_response, len(recent_messages)
        )

        suggestions = structured_response.suggestions
        state["suggested_questions"] = suggestions
        guide_logger.debug(f"Generated suggestions: {suggestions}")

        if suggestions:
            guide_logger.debug("--- Emitting suggestions ---")
            writer({"event": "suggestions", "data": suggestions})

    except Exception as e:
        print(f"Error generating or validating structured suggestions: {e}")

    return state
