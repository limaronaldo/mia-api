# GuideStreamWriter Documentation

## Overview

The `GuideStreamWriter` is a custom StreamWriter override designed specifically for LangGraph's custom streaming mode. It enhances the default LangGraph StreamWriter functionality while maintaining full compatibility with your existing ChatService streaming architecture. It provides additional capabilities for event logging, filtering, metadata injection, and debugging when used with the `@guide_agent` decorator.

## LangGraph Integration

This StreamWriter works seamlessly with your existing setup:
- LangGraph's `astream(stream_mode="custom")`
- ChatService event handling for: `validate_message_before_tool`, `validation_failed`, `suggestions`, `tool_start`, `tool_end`, `llm_message`
- Full backward compatibility with existing agent implementations

## Features

- **Event Interception**: Intercept and modify all events before they're emitted
- **Event Filtering**: Filter out specific event types
- **Metadata Enhancement**: Automatically add agent metadata to all events
- **Custom Event Emission**: Emit custom events with helper methods
- **Event Statistics**: Track and analyze event patterns
- **Debug Logging**: Enhanced logging for troubleshooting

## Basic Usage

### 1. Using with the @guide_agent Decorator

```python
from src.infrastructure.lib.ai.agent_decorator import guide_agent, create_langgraph_streaming_config

@guide_agent(
    agent_name="MyAgent",
    tools=my_tools,
    system_prompt=my_prompt,
    writer_config=create_langgraph_streaming_config()
)
async def my_agent(state: State, writer: StreamWriter, model: Runnable) -> dict:
    # The writer is now a GuideStreamWriter with enhanced capabilities

    # Standard usage works the same - events flow to ChatService
    writer({"event": "llm_message", "data": {"content": "Hello"}})

    return {"messages": []}
```

### 2. Service-Compatible Configuration

```python
from src.infrastructure.lib.ai.agent_decorator import create_service_compatible_config

# Fully compatible with your existing ChatService streaming
@guide_agent(
    agent_name="CompatibleAgent",
    writer_config=create_service_compatible_config()
)
async def compatible_agent(state: State, writer: StreamWriter, model: Runnable) -> dict:
    # All events pass through unchanged to ChatService
    # No metadata modification, no filtering
    pass
```

### 3. Enhanced Configuration with Filtering

```python
# Custom writer configuration
custom_config = {
    "filter_events": {"validate_message_before_tool"},  # Filter before ChatService
    "enhance_metadata": True,  # Add debug metadata
}

@guide_agent(
    agent_name="EnhancedAgent",
    writer_config=custom_config
)
async def enhanced_agent(state: State, writer: StreamWriter, model: Runnable) -> dict:
    # Validation events are filtered out, others pass to ChatService
    pass
```

## Advanced Features

### 1. LangGraph-Compatible Event Methods

```python
async def my_agent(state: State, writer: StreamWriter, model: Runnable) -> dict:
    guide_writer = GuideStreamWriter.get_guide_writer(writer)

    if guide_writer:
        # Use helper methods for events that ChatService handles
        guide_writer.emit_llm_message("Processing your request...")

        guide_writer.emit_tool_start(
            "search_properties",
            {"query": "luxury homes"},
            tool_call_id="call_123"
        )

        # Custom events (will show as warnings in ChatService but won't break)
        guide_writer.emit_custom_event("agent_started", {
            "timestamp": datetime.now().isoformat(),
            "session_id": state.get("thread_id")
        })
    else:
        # Fallback to standard writer
        writer({"event": "llm_message", "data": {"content": "Processing..."}})

    return {"messages": []}
```

### 2. Event Statistics and Monitoring

```python
async def my_agent(state: State, writer: StreamWriter, model: Runnable) -> dict:
    # Your agent logic here
    # ...

    # Get event statistics at the end
    guide_writer = GuideStreamWriter.get_guide_writer(writer)
    if guide_writer:
        stats = guide_writer.get_event_stats()

        print(f"Agent {stats['agent_name']} processed {stats['total_events']} events")
        print(f"Event breakdown: {stats['event_types']}")

        # Check which events are handled by your ChatService
        for event_type in stats['event_types']:
            if guide_writer.is_event_type_handled_by_service(event_type):
                print(f"✓ {event_type} - handled by ChatService")
            else:
                print(f"⚠ {event_type} - custom event (warning in service)")

    return {"messages": []}
```

### 3. Dynamic Event Filtering

```python
async def my_agent(state: State, writer: StreamWriter, model: Runnable) -> dict:
    guide_writer = GuideStreamWriter.get_guide_writer(writer)

    if guide_writer:
        # Add event filters dynamically
        if state.get("debug_mode"):
            guide_writer.remove_event_filter("validation_failed")
        else:
            guide_writer.add_event_filter("validation_failed")

    # Your agent logic
    # ...

    return {"messages": []}
```

## Configuration Options

### Writer Configuration Dictionary

```python
writer_config = {
    # Set of event names to filter out
    "filter_events": {"tool_start", "validate_message_before_tool"},

    # Whether to add agent metadata to all events (default: True)
    "enhance_metadata": True,

    # Whether to track event statistics (default: True)
    "enable_stats": True,
}
```

### Predefined Configurations

The module provides several predefined configurations:

#### LangGraph Streaming Configuration
```python
from src.infrastructure.lib.ai.agent_decorator import create_langgraph_streaming_config

# Optimal for LangGraph custom streaming with ChatService
config = create_langgraph_streaming_config()
# - No event filtering (all events reach ChatService)
# - Metadata enhancement for debugging
# - Statistics tracking enabled
```

#### Service Compatible Configuration
```python
from src.infrastructure.lib.ai.agent_decorator import create_service_compatible_config

# Zero modifications - full compatibility with existing ChatService
config = create_service_compatible_config()
# - No event filtering
# - No metadata modification
# - Minimal overhead
```

#### Debug Configuration
```python
from src.infrastructure.lib.ai.agent_decorator import create_debug_writer_config

# Optimal for development and debugging
config = create_debug_writer_config()
# - No event filtering
# - Full metadata enhancement
# - Statistics tracking enabled
```

#### Production Configuration
```python
from src.infrastructure.lib.ai.agent_decorator import create_production_writer_config

# Optimal for production environments
config = create_production_writer_config()
# - Filters validation_failed events
# - Minimal metadata overhead
# - Statistics disabled
```

#### Minimal Configuration
```python
from src.infrastructure.lib.ai.agent_decorator import create_minimal_writer_config

# Filters most events, minimal overhead
config = create_minimal_writer_config()
# - Filters tool_start and validate_message_before_tool
# - No metadata enhancement
# - No statistics tracking
```

## Event Types

The following event types are handled by your ChatService:

- `validate_message_before_tool`: Pre-tool validation events
- `validation_failed`: When validation fails
- `suggestions`: Suggestion generation events
- `tool_start`: When a tool execution begins
- `tool_end`: When a tool execution completes (with photo enrichment)
- `llm_message`: LLM response messages

Custom event types will show as warnings in ChatService logs but won't break the system.

## Enhanced Event Data

When `enhance_metadata` is enabled, all events will include additional fields in a `_agent_meta` object to avoid conflicts with ChatService event handling:

```json
{
  "event": "llm_message",
  "data": {
    "content": "Hello, world!",
    "_agent_meta": {
      "agent_name": "Broker",
      "event_sequence": 5
    }
  }
}
```

This design ensures ChatService continues to work with the original event structure while adding debug information.

## Best Practices

### 1. Environment-Specific Configurations

```python
import os

def get_writer_config():
    if os.getenv("ENVIRONMENT") == "production":
        return create_production_writer_config()
    elif os.getenv("DEBUG") == "true":
        return create_debug_writer_config()
    else:
        return create_minimal_writer_config()

@guide_agent(
    agent_name="AdaptiveAgent",
    writer_config=get_writer_config()
)
async def my_agent(state: State, writer: StreamWriter, model: Runnable) -> dict:
    pass
```

### 2. Conditional Custom Events

```python
async def my_agent(state: State, writer: StreamWriter, model: Runnable) -> dict:
    guide_writer = GuideStreamWriter.get_guide_writer(writer)

    if guide_writer and state.get("log_performance"):
        start_time = time.time()

        # Your agent logic
        result = await process_request(state)

        processing_time = time.time() - start_time
        guide_writer.emit_custom_event("performance_metric", {
            "processing_time": processing_time,
            "request_type": state.get("request_type")
        })

    return result
```

### 3. Error Handling and Fallbacks

```python
async def my_agent(state: State, writer: StreamWriter, model: Runnable) -> dict:
    try:
        # Your agent logic that might fail
        result = await risky_operation()

        # Success event
        if GuideStreamWriter.is_guide_writer(writer):
            writer.emit_custom_event("operation_success", {
                "operation": "risky_operation"
            })

        return result

    except Exception as e:
        # Failure event
        if GuideStreamWriter.is_guide_writer(writer):
            writer.emit_custom_event("operation_failed", {
                "operation": "risky_operation",
                "error": str(e)
            })

        # Fallback to standard writer behavior
        writer({"event": "error", "data": {"message": str(e)}})
        raise
```

## Migration Guide

### Existing Agents

To migrate existing agents to use the enhanced StreamWriter:

1. **No changes required for basic functionality** - existing code continues to work
2. **Add writer_config parameter** to the @guide_agent decorator if you want customization
3. **Optionally use enhanced features** like custom events and statistics

### Example Migration

**Before:**
```python
@guide_agent(agent_name="Broker", tools=chat_tools, system_prompt=system_prompt)
async def call_agent(state: State, writer: StreamWriter, model: Runnable) -> dict:
    # Existing implementation
    pass
```

**After (zero breaking changes):**
```python
@guide_agent(
    agent_name="Broker",
    tools=chat_tools,
    system_prompt=system_prompt,
    writer_config=create_service_compatible_config()  # Added - no behavior change
)
async def call_agent(state: State, writer: StreamWriter, model: Runnable) -> dict:
    # Existing implementation works unchanged
    # All events flow to ChatService exactly as before

    # Optional enhancements:
    guide_writer = GuideStreamWriter.get_guide_writer(writer)
    if guide_writer:
        # Enhanced tool events with proper structure
        if response.tool_calls:
            for tc in response.tool_calls:
                guide_writer.emit_tool_start(
                    tc.get("name"), tc.get("args"), tc.get("id")
                )

    # Rest of implementation unchanged...
    pass
```

## Troubleshooting

### Common Issues

1. **Writer not being overridden**: Ensure the `writer` parameter is correctly positioned (typically second parameter after `state`)

2. **Events being filtered unexpectedly**: Check your `filter_events` configuration

3. **Performance impact**: If experiencing performance issues, use `create_production_writer_config()` or disable `enhance_metadata`

### Debug Information

Enable debug logging to see all intercepted events:

```python
import logging
logging.getLogger('src.infrastructure.lib.logger').setLevel(logging.DEBUG)
```

This will show log messages like:
```
🔄 [AgentName] Event #1: tool_start
🔄 [AgentName] Event #2: tool_end
🚫 [AgentName] Filtered event: validate_message_before_tool
```
