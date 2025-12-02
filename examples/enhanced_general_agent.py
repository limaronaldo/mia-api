"""
Example showing how to enhance the existing general agent with GuideStreamWriter.

This example demonstrates:
1. How existing agents get enhanced automatically (no breaking changes)
2. How to use new helper methods for better event management
3. How to add custom events for better tracking
4. How to disable events when needed

The GuideStreamWriter is now injected by default - no migration needed!
"""

from textwrap import dedent
from typing import Any, Dict, List, Optional

from langchain_core.messages import BaseMessage, ToolMessage
from langchain_core.runnables import Runnable
from langgraph.types import StreamWriter

from src.infrastructure.ai.graphs.chat.state import State

# Import your existing tools and state
from src.infrastructure.ai.tools import chat_tools
from src.infrastructure.lib.ai.agent_decorator import guide_agent
from src.infrastructure.lib.verify_json_existance import verify_json_existence

system_prompt = dedent("""
    <agent>
        <identity>
            <name>Enhanced MBRAS Guide</name>
            <role>Luxury Real Estate Supervisor AI</role>
            <description>
            Enhanced version with improved event tracking and debugging capabilities.
            </description>
        </identity>

        <!-- Rest of your existing system prompt -->
    </agent>
""")


# EXAMPLE 1: Minimal migration - just add default enhanced writer
@guide_agent(agent_name="EnhancedBroker", tools=chat_tools, system_prompt=system_prompt)
async def enhanced_call_agent_minimal(
    state: State, writer: StreamWriter, model: Runnable
) -> dict:
    """
    Minimal enhancement - existing code works unchanged, but now gets enhanced writer.
    Writer is ALWAYS GuideStreamWriter - no need to check types!
    """
    print("---CALLING ENHANCED AGENT (MINIMAL)---")
    messages: List[BaseMessage] = state["messages"]

    # All your existing writer calls work exactly the same
    if messages and isinstance(messages[-1], ToolMessage):
        last_tool_message = messages[-1]
        tool_name = getattr(last_tool_message, "name", None)

        # This call works exactly as before, but now goes through GuideStreamWriter
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

    # Your existing model invocation
    response = await model.ainvoke({"messages": messages})

    if response.tool_calls:
        # Existing tool call handling works the same
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
    elif response.content and not verify_json_existence(response.content):
        writer({"event": "llm_message", "data": {"content": response.content}})

    messages.append(response)
    return {"messages": messages}


# EXAMPLE 2: Enhanced version with new capabilities
@guide_agent(
    agent_name="EnhancedBrokerPro",
    tools=chat_tools,
    system_prompt=system_prompt,
    writer_config={
        "enhance_metadata": True,  # Add agent metadata to all events
        "filter_events": set(),  # Don't filter any events
    },
)
async def enhanced_call_agent_pro(
    state: State, writer: StreamWriter, model: Runnable
) -> dict:
    """
    Enhanced version using new GuideStreamWriter capabilities.
    Shows how to use helper methods and custom events.
    """
    print("---CALLING ENHANCED AGENT (PRO)---")
    messages: List[BaseMessage] = state["messages"]
    loaded_memories: Optional[Dict[str, Any]] = state.get("loaded_memories")

    # Emit custom event for session tracking
    writer.emit_custom_event(
        "agent_session_start",
        {
            "thread_id": state.get("thread_id"),
            "user_id": state.get("user_id"),
            "has_memories": bool(loaded_memories),
            "message_count": len(messages),
        },
    )

    # Handle tool messages with enhanced events
    if messages and isinstance(messages[-1], ToolMessage):
        last_tool_message = messages[-1]
        tool_name = getattr(last_tool_message, "name", None)

        # Use helper method instead of manual event construction
        writer.emit_tool_end(
            tool_name=tool_name,
            output=last_tool_message.content,
            artifact=last_tool_message.artifact,
            tool_call_id=last_tool_message.tool_call_id,
            # Additional custom data
            processing_stage="post_tool_execution",
            message_sequence=len(messages),
        )

    # Track memory loading
    user_memory_str = "No relevant past interactions found for this conversation."
    if loaded_memories:
        memory_parts = []
        for schema_name, content in loaded_memories.items():
            memory_parts.append(f"### {schema_name} Memory\n{content}")
        user_memory_str = "\n\n".join(memory_parts)

        # Custom event for memory usage
        writer.emit_custom_event(
            "memory_loaded",
            {
                "memory_types": list(loaded_memories.keys()),
                "total_memory_length": len(user_memory_str),
                "memory_schemas": len(loaded_memories),
            },
        )

    # Model invocation with enhanced tracking
    try:
        response = await model.ainvoke(
            {"messages": messages, "user_memory": user_memory_str}
        )

        # Track successful model response
        writer.emit_custom_event(
            "model_response_success",
            {
                "has_tool_calls": bool(response.tool_calls),
                "has_content": bool(response.content),
                "response_type": "tool_calls" if response.tool_calls else "message",
            },
        )

    except Exception as e:
        # Track model errors
        writer.emit_custom_event(
            "model_response_error",
            {"error_type": type(e).__name__, "error_message": str(e)},
        )
        raise

    # Enhanced tool call handling
    if response.tool_calls:
        # Emit validation event if content exists
        if response.content:
            writer(
                {
                    "event": "validate_message_before_tool",
                    "data": {"content": response.content},
                }
            )

        # Use helper method for each tool call
        for tc in response.tool_calls:
            tc_dict = tc if isinstance(tc, dict) else tc.dict()
            tool_call_id = tc_dict.get("id") or getattr(tc, "id", None)

            writer.emit_tool_start(
                tool_name=tc_dict.get("name"),
                tool_input=tc_dict.get("args"),
                tool_call_id=tool_call_id,
                # Additional tracking data
                total_tool_calls=len(response.tool_calls),
                tool_sequence=response.tool_calls.index(tc) + 1,
            )

    elif response.content and not verify_json_existence(response.content):
        # Use helper method for LLM messages
        writer.emit_llm_message(
            content=response.content,
            # Additional context
            message_length=len(response.content),
            word_count=len(response.content.split()),
            has_memories=bool(loaded_memories),
        )

    messages.append(response)

    # Trim messages if needed
    MAX_MESSAGES = 30
    if len(messages) > MAX_MESSAGES:
        original_count = len(messages)
        messages = [messages[0]] + messages[-(MAX_MESSAGES - 1) :]

        # Track message trimming
        writer.emit_custom_event(
            "messages_trimmed",
            {
                "original_count": original_count,
                "trimmed_count": len(messages),
                "removed_count": original_count - len(messages),
            },
        )

    # Session completion event
    writer.emit_custom_event(
        "agent_session_complete",
        {
            "final_message_count": len(messages),
            "session_successful": True,
            "response_type": "tool_calls" if response.tool_calls else "message",
        },
    )

    # Get and log event statistics
    stats = writer.get_event_stats()
    print(f"Agent {stats['agent_name']} processed {stats['total_events']} events")
    print(f"Event breakdown: {stats['event_types']}")

    return {"messages": messages}


# EXAMPLE 3: Events disabled for minimal overhead
@guide_agent(
    agent_name="MinimalBroker",
    tools=chat_tools,
    system_prompt=system_prompt,
    events=False,  # Disable all events
)
async def minimal_call_agent(
    state: State, writer: StreamWriter, model: Runnable
) -> dict:
    """
    Version with events disabled - useful for testing or minimal overhead scenarios.
    All writer calls become no-ops.
    """
    print("---CALLING MINIMAL AGENT (NO EVENTS)---")
    messages: List[BaseMessage] = state["messages"]

    # All writer calls are no-ops when events=False
    writer({"event": "llm_message", "data": {"content": "This won't be emitted"}})
    writer.emit_custom_event("test_event", {"data": "This is ignored"})

    # Your business logic runs normally
    response = await model.ainvoke({"messages": messages})
    messages.append(response)

    return {"messages": messages}


# EXAMPLE 4: Conditional events based on environment
import os


@guide_agent(
    agent_name="ConditionalBroker",
    tools=chat_tools,
    system_prompt=system_prompt,
    events=os.getenv("ENABLE_EVENTS", "true").lower() == "true",
    writer_config={
        "enhance_metadata": os.getenv("DEBUG", "false").lower() == "true",
        "filter_events": {"validation_failed"}
        if os.getenv("ENVIRONMENT") == "production"
        else set(),
    },
)
async def conditional_call_agent(
    state: State, writer: StreamWriter, model: Runnable
) -> dict:
    """
    Environment-aware agent that adapts event behavior based on configuration.
    """
    print("---CALLING CONDITIONAL AGENT---")

    # Events are automatically enabled/disabled based on environment
    writer.emit_custom_event(
        "agent_start",
        {
            "environment": os.getenv("ENVIRONMENT", "development"),
            "debug_mode": os.getenv("DEBUG", "false").lower() == "true",
        },
    )

    # Your existing agent logic here...
    messages: List[BaseMessage] = state["messages"]
    response = await model.ainvoke({"messages": messages})
    messages.append(response)

    return {"messages": messages}


# MIGRATION CHECKLIST:
# ✅ No breaking changes - existing code works unchanged
# ✅ Writer is always GuideStreamWriter - no type checking needed
# ✅ All existing writer() calls continue to work
# ✅ New helper methods available: emit_llm_message, emit_tool_start, emit_tool_end, etc.
# ✅ Custom events: emit_custom_event() for tracking
# ✅ Event statistics: get_event_stats() for monitoring
# ✅ Event filtering: configure in writer_config
# ✅ Events can be disabled: events=False for minimal overhead
# ✅ Environment-aware configuration possible
