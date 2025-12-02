"""
Migration Comparison: Before and After GuideStreamWriter Integration

This file shows the exact difference between your existing general agent
and how it looks with the new enhanced GuideStreamWriter (with zero breaking changes).
"""

# =============================================================================
# BEFORE: Your existing general.py agent
# =============================================================================

from textwrap import dedent
from typing import Any, Dict, List, Optional

from langchain_core.messages import BaseMessage, ToolMessage
from langchain_core.runnables import Runnable
from langgraph.types import StreamWriter

from src.infrastructure.ai.graphs.chat.state import State
from src.infrastructure.ai.tools import chat_tools
from src.infrastructure.lib.ai.agent_decorator import guide_agent
from src.infrastructure.lib.verify_json_existance import verify_json_existence

system_prompt = dedent("""
    <agent>
        <identity>
            <name>MBRAS Guide</name>
            <role>Luxury Real Estate Supervisor AI</role>
            <!-- Your existing system prompt content -->
        </identity>
    </agent>
""")


# BEFORE - Your current decorator usage
@guide_agent(agent_name="Broker", tools=chat_tools, system_prompt=system_prompt)
async def call_agent_before(
    state: State, writer: StreamWriter, model: Runnable
) -> dict:
    """Your existing agent - BEFORE enhancement."""
    print("---CALLING AGENT---")
    messages: List[BaseMessage] = state["messages"]
    loaded_memories: Optional[Dict[str, Any]] = state.get("loaded_memories")

    # Your existing tool message handling
    if messages and isinstance(messages[-1], ToolMessage):
        last_tool_message = messages[-1]
        tool_name = getattr(last_tool_message, "name", None)
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

    # Your existing memory handling
    user_memory_str = "No relevant past interactions found for this conversation."
    if loaded_memories:
        memory_parts = []
        for schema_name, content in loaded_memories.items():
            memory_parts.append(f"### {schema_name} Memory\n{content}")
        user_memory_str = "\n\n".join(memory_parts)

    # Your existing model invocation
    response = await model.ainvoke(
        {"messages": messages, "user_memory": user_memory_str}
    )

    # Your existing tool call handling
    if response.tool_calls:
        if response.content:
            writer(
                {
                    "event": "validate_message_before_tool",
                    "data": {"content": response.content},
                }
            )

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

    # Your existing message trimming
    MAX_MESSAGES = 30
    if len(messages) > MAX_MESSAGES:
        messages = [messages[0]] + messages[-(MAX_MESSAGES - 1) :]

    return {"messages": messages}


# =============================================================================
# AFTER: Enhanced with GuideStreamWriter (NO BREAKING CHANGES)
# =============================================================================


# AFTER - Enhanced decorator usage (minimal change)
@guide_agent(agent_name="Broker", tools=chat_tools, system_prompt=system_prompt)
# ☝️ SAME decorator signature - but now writer is ALWAYS GuideStreamWriter!
async def call_agent_after_minimal(
    state: State, writer: StreamWriter, model: Runnable
) -> dict:
    """Your existing agent - AFTER enhancement (minimal changes)."""
    print("---CALLING ENHANCED AGENT---")
    messages: List[BaseMessage] = state["messages"]
    loaded_memories: Optional[Dict[str, Any]] = state.get("loaded_memories")

    # ✅ ALL your existing code works EXACTLY the same
    if messages and isinstance(messages[-1], ToolMessage):
        last_tool_message = messages[-1]
        tool_name = getattr(last_tool_message, "name", None)
        writer(  # ← Same call, but now enhanced with metadata and debugging
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

    user_memory_str = "No relevant past interactions found for this conversation."
    if loaded_memories:
        memory_parts = []
        for schema_name, content in loaded_memories.items():
            memory_parts.append(f"### {schema_name} Memory\n{content}")
        user_memory_str = "\n\n".join(memory_parts)

    response = await model.ainvoke(
        {"messages": messages, "user_memory": user_memory_str}
    )

    if response.tool_calls:
        if response.content:
            writer(  # ← Same call, enhanced automatically
                {
                    "event": "validate_message_before_tool",
                    "data": {"content": response.content},
                }
            )

        for tc in response.tool_calls:
            tc_dict = tc if isinstance(tc, dict) else tc.dict()
            tool_call_id = tc_dict.get("id") or getattr(tc, "id", None)
            writer(  # ← Same call, enhanced automatically
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

    MAX_MESSAGES = 30
    if len(messages) > MAX_MESSAGES:
        messages = [messages[0]] + messages[-(MAX_MESSAGES - 1) :]

    return {"messages": messages}


# =============================================================================
# AFTER: Enhanced with new features (OPTIONAL improvements)
# =============================================================================


@guide_agent(
    agent_name="Broker",
    tools=chat_tools,
    system_prompt=system_prompt,
    # 🆕 Optional: Add configuration for enhanced features
    writer_config={
        "enhance_metadata": True,  # Add agent info to all events
        "filter_events": set(),  # Don't filter any events
    },
)
async def call_agent_after_enhanced(
    state: State, writer: StreamWriter, model: Runnable
) -> dict:
    """Your existing agent - AFTER enhancement with NEW features."""
    print("---CALLING SUPER ENHANCED AGENT---")
    messages: List[BaseMessage] = state["messages"]
    loaded_memories: Optional[Dict[str, Any]] = state.get("loaded_memories")

    # 🆕 NEW: Custom event tracking (completely optional)
    writer.emit_custom_event(
        "broker_session_start",
        {
            "thread_id": state.get("thread_id"),
            "user_id": state.get("user_id"),
            "has_memories": bool(loaded_memories),
        },
    )

    # ✅ All existing code still works exactly the same
    if messages and isinstance(messages[-1], ToolMessage):
        last_tool_message = messages[-1]
        tool_name = getattr(last_tool_message, "name", None)

        # 🆕 OPTIONAL: Use helper method instead of manual construction
        writer.emit_tool_end(
            tool_name=tool_name,
            output=last_tool_message.content,
            artifact=last_tool_message.artifact,
            tool_call_id=last_tool_message.tool_call_id,
        )
        # OR keep using the old way - both work!
        # writer({"event": "tool_end", "data": {...}})

    user_memory_str = "No relevant past interactions found for this conversation."
    if loaded_memories:
        memory_parts = []
        for schema_name, content in loaded_memories.items():
            memory_parts.append(f"### {schema_name} Memory\n{content}")
        user_memory_str = "\n\n".join(memory_parts)

        # 🆕 NEW: Track memory usage
        writer.emit_custom_event(
            "memory_loaded",
            {
                "schemas": list(loaded_memories.keys()),
                "total_length": len(user_memory_str),
            },
        )

    response = await model.ainvoke(
        {"messages": messages, "user_memory": user_memory_str}
    )

    if response.tool_calls:
        if response.content:
            writer(
                {
                    "event": "validate_message_before_tool",
                    "data": {"content": response.content},
                }
            )

        for tc in response.tool_calls:
            tc_dict = tc if isinstance(tc, dict) else tc.dict()
            tool_call_id = tc_dict.get("id") or getattr(tc, "id", None)

            # 🆕 OPTIONAL: Use helper method
            writer.emit_tool_start(
                tool_name=tc_dict.get("name"),
                tool_input=tc_dict.get("args"),
                tool_call_id=tool_call_id,
            )
            # OR keep the old way - both work!

    elif response.content and not verify_json_existence(response.content):
        # 🆕 OPTIONAL: Use helper method
        writer.emit_llm_message(response.content)
        # OR keep the old way: writer({"event": "llm_message", "data": {"content": response.content}})

    messages.append(response)

    MAX_MESSAGES = 30
    if len(messages) > MAX_MESSAGES:
        messages = [messages[0]] + messages[-(MAX_MESSAGES - 1) :]

    # 🆕 NEW: Get event statistics for monitoring
    stats = writer.get_event_stats()
    print(f"Agent processed {stats['total_events']} events: {stats['event_types']}")

    return {"messages": messages}


# =============================================================================
# MIGRATION SUMMARY
# =============================================================================

"""
MIGRATION FROM YOUR CURRENT general.py TO ENHANCED VERSION:

✅ ZERO BREAKING CHANGES:
   - Your exact same code works without any modifications
   - Same decorator signature: @guide_agent(agent_name="Broker", tools=chat_tools, system_prompt=system_prompt)
   - Same function signature: async def call_agent(state: State, writer: StreamWriter, model: Runnable) -> dict
   - All writer() calls work exactly the same

🚀 AUTOMATIC ENHANCEMENTS:
   - Writer is now ALWAYS GuideStreamWriter (enhanced with debugging, metadata, filtering)
   - Events get automatic agent metadata injection (optional)
   - Enhanced logging and debugging capabilities
   - Event statistics tracking

🆕 NEW OPTIONAL FEATURES:
   - Helper methods: writer.emit_llm_message(), writer.emit_tool_start(), writer.emit_tool_end()
   - Custom events: writer.emit_custom_event("event_name", {data})
   - Event filtering: Configure in writer_config to filter out specific events
   - Statistics: writer.get_event_stats() for monitoring
   - Events can be disabled: events=False for minimal overhead

📋 TO MIGRATE YOUR CURRENT general.py:
   1. Change nothing - it works as-is with enhancements
   2. Optionally add writer_config for custom behavior
   3. Optionally use new helper methods for cleaner code
   4. Optionally add custom events for better tracking

🔧 CONFIGURATION OPTIONS:
   @guide_agent(
       agent_name="Broker",
       tools=chat_tools,
       system_prompt=system_prompt,
       events=True,  # Default: True (can disable with False)
       writer_config={
           "enhance_metadata": True,     # Add agent info to events
           "filter_events": set(),       # Events to filter out
           "enable_stats": True,         # Track event statistics
       }
   )

Your ChatService streaming code remains unchanged and continues to work perfectly!
"""
