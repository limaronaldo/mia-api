import inspect
from typing import Callable, List, Literal, Optional, Type

from langchain_core.messages import BaseMessage, ToolMessage
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import END, StateGraph
from langgraph.graph.state import RunnableConfig
from langgraph.prebuilt import ToolNode
from langgraph.runtime import get_runtime
from pydantic import BaseModel

from src.infrastructure.ai.models.gemini import (
    gemini_2_5_flash,
    gemini_2_5_pro,
)
from src.infrastructure.ai.tools.handoffs import create_task_description_handoff_tool
from src.infrastructure.lib.ai.messages import AIHelpingMessages
from src.infrastructure.lib.logger import guide_logger
from src.infrastructure.lib.verify_json_existance import verify_json_existence

type Model = Literal["standard", "heavy", "lite"]


_AGENT_REGISTRY = {}
_AGENT_SYSTEM_PROMPTS = {}
_SPECTATOR_AGENTS = set()


def register_agent(
    name: str, description: str, system_prompt: str = None, spectator_mode: bool = False
):
    """Register an agent with its description and system prompt for partner tool creation."""
    _AGENT_REGISTRY[name] = description
    if system_prompt:
        _AGENT_SYSTEM_PROMPTS[name] = system_prompt
    if spectator_mode:
        _SPECTATOR_AGENTS.add(name)
    guide_logger.debug(f"Registered agent '{name}' with description: {description}")


def get_agent_description(name: str) -> str:
    """Get the description of a registered agent."""
    return _AGENT_REGISTRY.get(name, f"{name} agent for specialized assistance")


def get_registered_agents() -> dict:
    """Get all registered agents and their descriptions."""
    return _AGENT_REGISTRY.copy()


def clear_agent_registry():
    """Clear the agent registry (useful for testing)."""
    global _AGENT_REGISTRY, _AGENT_SYSTEM_PROMPTS, _SPECTATOR_AGENTS
    _AGENT_REGISTRY.clear()
    _AGENT_SYSTEM_PROMPTS.clear()
    _SPECTATOR_AGENTS.clear()
    guide_logger.debug("Agent registry cleared")


def is_agent_registered(name: str) -> bool:
    """Check if an agent is registered."""
    return name in _AGENT_REGISTRY


def get_agent_system_prompt(name: str) -> str:
    """Get the system prompt of a registered agent."""
    return _AGENT_SYSTEM_PROMPTS.get(name, "")


def get_all_agent_system_prompts() -> dict:
    """Get all registered agents and their system prompts."""
    return _AGENT_SYSTEM_PROMPTS.copy()


def is_spectator_agent(name: str) -> bool:
    """Check if an agent is in spectator mode."""
    return name in _SPECTATOR_AGENTS


def get_spectator_agents() -> set:
    """Get all spectator agents."""
    return _SPECTATOR_AGENTS.copy()


def get_model(model: Model):
    match model:
        case "standard":
            _model = gemini_2_5_flash
        case "heavy":
            _model = gemini_2_5_pro
        case "lite":
            from src.infrastructure.ai.models.gemini import gemini_2_5_flash_lite

            _model = gemini_2_5_flash_lite

    return _model


def guide_agent(
    agent_name: str,
    model: Model = "heavy",
    tools: list[Callable] = [],
    system_prompt: str = "",
    custom_prompt_template: Optional[ChatPromptTemplate] = None,
    response_model: Optional[Type[BaseModel]] = None,
    partners: List[str] = [],
    create_graph: bool = False,
    state_class=None,
    description: str = "",
    spectator_mode: bool = False,
):
    """
    General decorator for guide agents that handles basic response infrastructure.
    Can create isolated graphs for each agent or work within existing graph systems.

    Args:
        agent_name: Name of the agent for logging and identification
        model: Model type to use ("standard", "heavy", or "lite")
        tools: List of tools to bind to the model
        system_prompt: System prompt template (used if custom_prompt_template is None)
        custom_prompt_template: Custom ChatPromptTemplate for full prompt customization
        response_model: Pydantic model for automatic structured output
        partners: List of partner agent names (snake_cased) to create handoff tools for
        create_graph: Whether to create an isolated graph for this agent
        state_class: State class to use for the graph (required if create_graph=True)
        description: Description of what this agent does (used in partner transfer instructions)
        spectator_mode: If True, this agent won't be tracked as current_agent (useful for validation, monitoring agents)

    Agent Function Parameters:
        The decorated function can accept these optional parameters:
        - state: The current state (always first parameter)
        - writer: StreamWriter for event emission
        - model: The chained model (prompt + base model + tools, with structured output if response_model provided)
        - base_model: The raw base model (supports all original methods like with_structured_output)
        - prompt_template: The ChatPromptTemplate being used

    Returns:
        If create_graph=True: Returns compiled graph
        If create_graph=False: Returns decorated function for use in existing graphs
    """

    def decorator(func):
        if description:
            register_agent(agent_name, description, system_prompt, spectator_mode)

        enhanced_system_prompt = system_prompt
        if partners:
            partner_descriptions = []
            for partner in partners:
                partner_desc = get_agent_description(partner)
                partner_descriptions.append(f"- transfer_to_{partner}: {partner_desc}")

            partner_instructions = f"""

        <IMPORTANT_PARTNER_GUIDELINES>
        You have access to specialized partner agents: {", ".join(partners)}.

        CRITICAL: If a user's question or request is related to any of these specialized areas, you MUST transfer the conversation to the appropriate partner agent using the transfer_to_[partner_name] tool.

        Available transfers:
        {chr(10).join(partner_descriptions)}

        Always provide a comprehensive task_description when transferring, including:
        - Complete context of the user's request
        - Relevant conversation history
        - Specific requirements or preferences mentioned
        - Any important details the partner agent needs to know

        Do NOT attempt to handle specialized requests yourself when a partner agent is available.
        </IMPORTANT_PARTNER_GUIDELINES>"""
            enhanced_system_prompt = system_prompt + partner_instructions

        if custom_prompt_template:
            MODEL_PROMPT_TEMPLATE = custom_prompt_template
        else:
            MODEL_PROMPT_TEMPLATE = ChatPromptTemplate.from_messages(
                [
                    ("system", enhanced_system_prompt),
                    ("placeholder", "{messages}"),
                ]
            )
        base_model_instance = get_model(model)

        handoff_tools = []
        for partner_name in partners:
            partner_desc = get_agent_description(partner_name)
            handoff_tool = create_task_description_handoff_tool(
                agent_name=partner_name,
                description=f"Transfer to {partner_name}: {partner_desc}",
            )
            handoff_tools.append(handoff_tool)

        all_tools = tools + handoff_tools

        if response_model:
            structured_model = base_model_instance.with_structured_output(
                response_model
            )
            _model = MODEL_PROMPT_TEMPLATE | structured_model
        else:
            _model = MODEL_PROMPT_TEMPLATE | base_model_instance.bind_tools(all_tools)

        async def async_wrapper(*args, config: RunnableConfig, **kwargs):
            guide_logger.debug(f"🧠 [{agent_name}] [{model}] Calling")

            try:
                runtime = get_runtime()
                writer = runtime.stream_writer
            except Exception as e:
                guide_logger.warning(
                    f"⚠️ [{agent_name}] Could not get LangGraph runtime: {e}"
                )

                def writer(data):
                    guide_logger.debug(
                        f"[{agent_name}] No-op writer - would emit: {data}"
                    )

            state = args[0] if args else {}
            messages: List[BaseMessage] = state.get("messages", [])
            retry_context = state.get("retry_context")

            if not spectator_mode and state.get("current_agent") != agent_name:
                guide_logger.debug(
                    f"[{agent_name}] Setting current_agent from '{state.get('current_agent')}' to '{agent_name}'"
                )
                state["current_agent"] = agent_name
            elif spectator_mode:
                guide_logger.debug(
                    f"[{agent_name}] Spectator mode - preserving current_agent: '{state.get('current_agent')}'"
                )

            if messages and isinstance(messages[-1], ToolMessage):
                last_tool_message = messages[-1]
                tool_name = getattr(last_tool_message, "name", None)
                guide_logger.debug(f"--- Tool end event emitted for tool '{tool_name}'")
                writer(
                    {
                        "event": "tool_end",
                        "data": {
                            "name": tool_name,
                            "output": last_tool_message.content,
                            "artifact": last_tool_message.artifact,
                            "tool_call_id": last_tool_message.tool_call_id,
                        },
                    }
                )

            retry_context_used = False
            messages_for_llm = list(messages)

            if retry_context:
                failed_attempt = retry_context.get("failed_attempt", "N/A")
                feedback = retry_context.get("feedback", "N/A")
                retry_count = retry_context.get("retry_count", 0)

                guide_logger.info(
                    f"[{agent_name}] Injecting retry context (attempt {retry_count + 1}). "
                    f"Feedback: {feedback[:100]}..."
                )

                tool_error_context = ""
                for msg in reversed(messages[-5:]):
                    if isinstance(msg, ToolMessage) and "Error:" in str(msg.content):
                        tool_error_context = (
                            f"\n\nRECENT TOOL ERROR: {msg.content[:200]}..."
                        )
                        break

                retry_message = AIHelpingMessages.retry_message(
                    feedback, failed_attempt, tool_error_context
                )
                messages_for_llm.append(retry_message)
                retry_context_used = True

            enhanced_state = {**state, "messages": messages_for_llm}

            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())

            agent_kwargs = {}
            if "writer" in param_names:
                agent_kwargs["writer"] = writer
            if "model" in param_names:
                agent_kwargs["model"] = _model
            if "base_model" in param_names:
                agent_kwargs["base_model"] = base_model_instance
            if "prompt_template" in param_names:
                agent_kwargs["prompt_template"] = MODEL_PROMPT_TEMPLATE

            response = await func(enhanced_state, config, **agent_kwargs)

            if hasattr(response, "tool_calls") and response.tool_calls:
                guide_logger.debug(
                    "Emitting validate_message_before_tool (if content exists)"
                )
                guide_logger.debug(response.tool_calls)

                if response.content:
                    writer(
                        {
                            "event": "validate_message_before_tool",
                            "data": {"content": response.content},
                        }
                    )

                guide_logger.debug("Emitting tool_start events")
                for tc in response.tool_calls:
                    tc_dict = tc if isinstance(tc, dict) else tc.dict()
                    tool_call_id = tc_dict.get("id") or getattr(tc, "id", None)
                    writer(
                        {
                            "event": "tool_start",
                            "data": {
                                "name": tc_dict.get("name"),
                                "input": tc_dict.get("args"),
                                "tool_call_id": tool_call_id,
                            },
                        }
                    )

                messages.append(response)

            elif hasattr(response, "content") and response.content:
                if not retry_context and not verify_json_existence(response.content):
                    guide_logger.debug(response.content)
                    guide_logger.debug("Emitting llm_message event")
                    writer(
                        {"event": "llm_message", "data": {"content": response.content}}
                    )
                elif retry_context:
                    guide_logger.debug("Emitting retry_context event")
                else:
                    guide_logger.error("Emitting no_content event")
                    writer(
                        {"event": "no_content", "data": {"content": response.content}}
                    )

                messages.append(response)

            elif isinstance(response, dict) and "messages" in response:
                messages = response["messages"]
            else:
                guide_logger.warning(
                    f"[{agent_name}] Unexpected response format: {type(response)}"
                )

            MAX_MESSAGES = 30
            if len(messages) > MAX_MESSAGES:
                messages = [messages[0]] + messages[-(MAX_MESSAGES - 1) :]
                guide_logger.trace(f"Trimmed messages list to {len(messages)} items.")

            return_state = {"messages": messages}

            if not spectator_mode:
                return_state["current_agent"] = agent_name

            essential_keys = ["loaded_memories", "suggested_questions"]
            for key in essential_keys:
                if key in state:
                    return_state[key] = state[key]

            if retry_context_used:
                guide_logger.trace("Clearing retry context from state.")
                return_state["retry_context"] = None

            if isinstance(response, dict):
                for key, value in response.items():
                    if key != "messages":
                        return_state[key] = value

            return return_state

        async_wrapper._original_func = func
        async_wrapper._agent_config = {
            "agent_name": agent_name,
            "model": model,
            "tools": all_tools,
            "system_prompt": enhanced_system_prompt,
            "custom_prompt_template": custom_prompt_template,
            "response_model": response_model,
            "partners": partners,
            "description": description,
        }

        if create_graph and state_class:
            return _create_agent_graph(
                async_wrapper, state_class, agent_name, all_tools
            )

        return async_wrapper

    return decorator


def _create_agent_graph(
    agent_func, state_class, agent_name: str, tools: List[Callable]
):
    """Create an isolated graph for a single agent with full flow control."""

    def should_continue(state) -> Literal["tools", "validator", "__end__"]:
        """Determine next step after agent execution."""
        last_message = state["messages"][-1]

        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        elif hasattr(last_message, "content") and last_message.content:
            return "validator"
        return END

    def validate_response(state):
        """Simple response validation - can be extended."""
        messages = state.get("messages", [])
        if messages:
            last_message = messages[-1]
            if hasattr(last_message, "content") and last_message.content:
                if not verify_json_existence(last_message.content):
                    guide_logger.debug(
                        f"[{agent_name}] Response validated successfully"
                    )
                    return {"messages": messages}
        return {"messages": messages}

    def handle_retry(state):
        """Handle retry logic for failed responses."""
        retry_context = state.get("retry_context")
        if retry_context:
            guide_logger.debug(f"[{agent_name}] Handling retry context")
        return state

    graph = StateGraph(state_class)

    graph.add_node("agent", agent_func)
    graph.add_node("tools", ToolNode(tools=tools))
    graph.add_node("validator", validate_response)
    graph.add_node("retry_handler", handle_retry)

    graph.set_entry_point("agent")

    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "validator": "validator",
            "__end__": END,
        },
    )

    graph.add_edge("tools", "agent")

    graph.add_conditional_edges(
        "validator",
        lambda state: "retry_handler" if state.get("retry_context") else END,
        {
            "retry_handler": "retry_handler",
            END: END,
        },
    )

    graph.add_edge("retry_handler", "agent")

    compiled_graph = graph.compile()

    compiled_graph._agent_name = agent_name
    compiled_graph._agent_tools = [
        getattr(tool, "name", getattr(tool, "__name__", str(tool))) for tool in tools
    ]

    guide_logger.info(
        f"🔗 Created isolated graph for agent '{agent_name}' with {len(tools)} tools"
    )

    return compiled_graph


def create_multi_agent_system(agents: List, state_class, checkpointer=None):
    """
    Create a multi-agent system where agents can handoff to each other.

    Args:
        agents: List of agent functions created with @guide_agent
        state_class: State class for the system
        checkpointer: Optional checkpointer for persistence

    Returns:
        Compiled graph with all agents and handoff capabilities
    """
    graph = StateGraph(state_class)

    agent_names = []

    for agent_func in agents:
        if hasattr(agent_func, "_agent_config"):
            config = agent_func._agent_config
            agent_name = config["agent_name"]
            agent_names.append(agent_name)

            graph.add_node(agent_name, agent_func)

            tools = config.get("tools", [])
            if tools:
                tools_node_name = f"{agent_name}_tools"
                graph.add_node(tools_node_name, ToolNode(tools=tools))

    def route_after_agent(state, agent_name: str):
        """Route after agent execution - can go to tools, other agents, or end."""
        last_message = state["messages"][-1]

        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            for tool_call in last_message.tool_calls:
                tool_name = tool_call.get("name", "")
                if tool_name.startswith("transfer_to_"):
                    target_agent = tool_name.replace("transfer_to_", "")
                    if target_agent in agent_names:
                        guide_logger.debug(
                            f"Handoff from {agent_name} to {target_agent}"
                        )
                        return target_agent

            return f"{agent_name}_tools"

        return END

    for agent_name in agent_names:

        def make_router(name):
            return lambda state: route_after_agent(state, name)

        routing_options = {f"{agent_name}_tools": f"{agent_name}_tools", END: END}

        for other_agent in agent_names:
            if other_agent != agent_name:
                routing_options[other_agent] = other_agent

        graph.add_conditional_edges(
            agent_name, make_router(agent_name), routing_options
        )

        if f"{agent_name}_tools" in [node for node in graph.nodes]:
            graph.add_edge(f"{agent_name}_tools", agent_name)

    if agent_names:
        graph.set_entry_point(agent_names[0])

    compiled_graph = graph.compile(checkpointer=checkpointer)

    guide_logger.info(
        f"🌐 Created multi-agent system with agents: {', '.join(agent_names)}"
    )

    return compiled_graph
